from datetime import date, datetime, timezone
from dataclasses import replace

import pytest

from src.common.schemas import QualFeature, QuantFeature, join_features
from src.common.dates import horizon_date, next_execution_open, outcome_complete
from src.genai.chunking import chunk_document
from src.genai.retrieval import FilingIndex
from src.genai.scoring import mock_score
from src.genai.sec_ingestion import parse_filings
from scripts.genai.ingest_filings import ingest_one


def sample_record():
    return {"ticker": "NVDA", "accession_number": "0001045810-21-000205",
            "filing_date": "2021-11-19", "source_url": "https://www.sec.gov/example",
            "first_eligible_at": "2021-11-22T14:30:00+00:00",
            "sections": {"management_discussion": "Revenue grew from data center demand.",
                         "risk_factors": "Supply constraints can limit shipments."}}


def test_chunk_ids_are_stable_and_missing_sections_are_empty():
    record = sample_record()
    a = chunk_document(record, chunk_words=5, overlap_words=1)
    assert a == chunk_document(record, chunk_words=5, overlap_words=1)
    assert all(c["accession_number"] == record["accession_number"] for c in a)
    record["sections"]["risk_factors"] = ""
    assert all(c["section"] != "risk_factors" for c in chunk_document(record, chunk_words=5, overlap_words=1))
    record["first_eligible_at"] = None
    with pytest.raises(ValueError):
        chunk_document(record, chunk_words=5, overlap_words=1)


def test_retrieval_applies_historical_filter_to_query():
    class FakeCollection:
        def query(self, **kwargs):
            self.kwargs = kwargs
            return {"documents": [["Historical text"]], "metadatas": [[{
                "ticker": "NVDA", "section": "risk_factors", "source_url": "https://www.sec.gov/example",
                "accession_number": "0001045810-21-000205"}]], "distances": [[0.2]]}
    index = object.__new__(FilingIndex)
    index.collection = FakeCollection()
    index.embedder = type("Embed", (), {"encode": lambda self, texts: [[0.1, 0.2]]})()
    cutoff = datetime(2022, 1, 3, 14, 30, tzinfo=timezone.utc)
    passages = index.search("risk", ticker="NVDA", cutoff=cutoff, section="risk_factors",
                            lookback_months=24)
    clauses = index.collection.kwargs["where"]["$and"]
    assert {"first_eligible_epoch": {"$lte": int(cutoff.timestamp())}} in clauses
    assert {"ticker": {"$eq": "NVDA"}} in clauses
    assert {"section": {"$eq": "risk_factors"}} in clauses
    assert any("first_eligible_epoch" in c and "$gte" in c["first_eligible_epoch"] for c in clauses)
    assert passages[0]["metadata"]["accession_number"] == "0001045810-21-000205"


def test_chroma_persists_and_excludes_future_before_ranking(tmp_path):
    pytest.importorskip("chromadb")
    class Embed:
        def encode(self, texts):
            return [[1.0, 0.0] for _ in texts]
    historic = chunk_document(sample_record(), chunk_words=20, overlap_words=0)[0]
    future_record = sample_record()
    future_record["accession_number"] = "0001045810-22-000021"
    future_record["first_eligible_at"] = "2022-02-17T14:30:00+00:00"
    future = chunk_document(future_record, chunk_words=20, overlap_words=0)[0]
    stale_record = sample_record()
    stale_record["accession_number"] = "0001045810-16-000001"
    stale_record["first_eligible_at"] = "2016-11-22T14:30:00+00:00"
    stale = chunk_document(stale_record, chunk_words=20, overlap_words=0)[0]
    index = FilingIndex(tmp_path, Embed())
    index.upsert([historic, future, stale])
    index.upsert([historic])
    reopened = FilingIndex(tmp_path, Embed())
    assert reopened.collection.count() == 3
    found = reopened.search("revenue", ticker="NVDA",
                            cutoff=datetime(2022, 1, 3, 14, 30, tzinfo=timezone.utc),
                            top_k=5, lookback_months=24)
    assert {p["metadata"]["accession_number"] for p in found} == {"0001045810-21-000205"}


def test_mock_score_and_synthetic_quant_join():
    evidence = [{"text": "Historical text", "metadata": {
        "accession_number": "0001045810-21-000205", "section": "risk_factors",
        "source_url": "https://www.sec.gov/example",
        "first_eligible_at": "2021-11-22T14:30:00+00:00"}}]
    qualitative = mock_score("NVDA", date(2022, 1, 3), evidence, top_k=5)
    assert qualitative.metadata["status"] == "mock_only"
    assert qualitative.qualitative_score == 0.5
    quant = QuantFeature("NVDA", date(2022, 1, 3), 0.7,
                         datetime(2021, 12, 31, tzinfo=timezone.utc), {"fixture": "synthetic"})
    cutoff = datetime(2022, 1, 3, 14, 30, tzinfo=timezone.utc)
    assert join_features(quant, qualitative, cutoff)["quant_score"] == 0.7
    with pytest.raises(ValueError):
        QualFeature("NVDA", date(2022, 1, 3), 1.1, (), (), {})
    assert mock_score("NVDA", date(2022, 1, 3), [], top_k=5).qualitative_score is None
    with pytest.raises(ValueError):
        join_features(quant, mock_score("AAPL", date(2022, 1, 3), [], top_k=5), cutoff)
    with pytest.raises(ValueError):
        join_features(quant, qualitative, datetime(2021, 1, 1, tzinfo=timezone.utc))


def test_execution_and_forward_outcome_are_separate():
    def weekday_open(day):
        if day.weekday() >= 5:
            return None
        return datetime(day.year, day.month, day.day, 14, 30, tzinfo=timezone.utc)
    cutoff = datetime(2022, 1, 3, 14, 30, tzinfo=timezone.utc)
    assert next_execution_open(cutoff, weekday_open).date() == date(2022, 1, 4)
    assert horizon_date(date(2020, 2, 29), 12) == date(2021, 2, 28)
    assert not outcome_complete(date(2022, 1, 3), 12, date(2022, 12, 30), weekday_open)
    assert outcome_complete(date(2022, 1, 3), 12, date(2023, 1, 3), weekday_open)


def test_mocked_filing_to_provenance_slice(tmp_path):
    pytest.importorskip("chromadb")
    table = {"accessionNumber": ["0001045810-21-000205"], "form": ["10-Q"],
             "filingDate": ["2021-11-19"], "acceptanceDateTime": ["2021-11-19T17:01:00"],
             "primaryDocument": ["nvda-20211031.htm"]}
    filing = replace(parse_filings("NVDA", "0001045810", table, {"10-Q"})[0],
                     first_eligible_at="2021-11-22T14:30:00+00:00")
    raw = b"<html><p>Item 2. Management's Discussion and Analysis</p><p>Revenue improved.</p><p>Item 3. Market Risk</p><p>Item 1A. Risk Factors</p><p>Supply risk.</p><p>Item 2. Other Information</p></html>"
    class FakeClient:
        calls = 0
        def get(self, url):
            self.calls += 1
            assert url == filing.source_url
            return raw
    client = FakeClient()
    record = ingest_one(client, filing, tmp_path)
    assert ingest_one(client, filing, tmp_path) == record
    assert client.calls == 1
    chunks = chunk_document(record, chunk_words=20, overlap_words=0)
    class Embed:
        def encode(self, texts):
            return [[1.0, 0.0] for _ in texts]
    index = FilingIndex(tmp_path / "chroma", Embed())
    index.upsert(chunks)
    passages = index.search("revenue", ticker="NVDA",
                            cutoff=datetime(2022, 1, 3, 14, 30, tzinfo=timezone.utc))
    result = mock_score("NVDA", date(2022, 1, 3), passages, top_k=5)
    assert record["extraction_status"] == "complete"
    assert result.filing_accessions == ("0001045810-21-000205",)
    assert all(e["source_url"] == filing.source_url for e in result.evidence)
