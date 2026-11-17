from datetime import date, datetime, time, timezone
import json

import pytest

from src.genai.filing_parser import extract_sections
from src.genai.sec_ingestion import (SecClient, acceptance_timestamp, decision_cutoff,
                                      eligible_filings, first_eligible_open, is_available,
                                      latest_report_set, parse_filings, resolve_cik, save_filing)


def weekday_open(day):
    if day.weekday() >= 5:
        return None
    return datetime.combine(day, time(14, 30), timezone.utc)


def table():
    return {"accessionNumber": ["0001045810-21-000205", "0001045810-22-000021", "bad"],
            "form": ["10-Q", "10-K", "10-Q"],
            "filingDate": ["2021-11-19", "2022-02-16", "2021-12-01"],
            "acceptanceDateTime": ["2021-11-19T17:01:00", "2022-02-16T16:00:00", ""],
            "primaryDocument": ["nvda-20211031.htm", "nvda-20220130.htm", "bad.htm"]}


def test_cik_and_metadata():
    assert resolve_cik("nvda", {"0": {"ticker": "NVDA", "cik_str": 1045810}}) == "0001045810"
    with pytest.raises(KeyError):
        resolve_cik("NONE", {})
    rejections = []
    filings = parse_filings("nvda", "0001045810", table(), {"10-K", "10-Q"}, rejections)
    assert len(filings) == 2
    assert rejections == [{"ticker": "NVDA", "accession_number": "bad",
                           "reason": "unknown_or_ambiguous_acceptance_time"}]
    assert filings[0].source_url.endswith("/1045810/000104581021000205/nvda-20211031.htm")
    assert filings[0].filing_available_at == "2021-11-19T17:01:00-05:00"


def test_cutoff_excludes_future_and_unknown():
    cutoff = decision_cutoff(date(2022, 1, 3))
    assert is_available("2021-11-19T17:01:00-05:00", cutoff)
    assert not is_available("2022-02-16T16:00:00-05:00", cutoff)
    assert not is_available("2022-01-03T09:30:00-05:00", cutoff)
    assert not is_available("2022-01-02T12:00:00", cutoff)
    assert not is_available(None, cutoff)
    assert acceptance_timestamp("garbage") is None
    assert acceptance_timestamp("2021-11-07T01:30:00") is None


def test_eligible_filings_uses_historical_cutoff():
    class Fake:
        def get_json(self, url):
            if "company_tickers" in url:
                return {"0": {"ticker": "NVDA", "cik_str": 1045810}}
            return {"filings": {"recent": table(), "files": []}}
    found = eligible_filings(Fake(), "NVDA", decision_cutoff(date(2022, 1, 3)),
                            {"10-K", "10-Q"}, session_open=weekday_open)
    assert [f.accession_number for f in found] == ["0001045810-21-000205"]
    assert found[0].first_eligible_at == "2021-11-22T14:30:00+00:00"


def test_next_regular_open_and_latest_report_set():
    assert first_eligible_open("2022-01-03T08:00:00-05:00", weekday_open) == "2022-01-03T14:30:00+00:00"
    assert first_eligible_open("2021-11-19T17:01:00-05:00", weekday_open) == "2021-11-22T14:30:00+00:00"
    assert first_eligible_open("2022-01-03T09:30:00-05:00", weekday_open) == "2022-01-04T14:30:00+00:00"
    filings = parse_filings("NVDA", "0001045810", table(), {"10-K", "10-Q"})
    assert latest_report_set(filings) == [filings[1]]


def test_cache_and_structured_sections(tmp_path):
    filing = parse_filings("NVDA", "0001045810", table(), {"10-Q"})[0]
    raw = b"<html><p>Item 2. Management's Discussion and Analysis</p><p>Revenue improved.</p><p>Item 3. Market Risk</p><p>Item 1A. Risk Factors</p><p>Supply risk.</p><p>Item 2. Other Information</p></html>"
    class Fake:
        calls = 0
        def get(self, url):
            self.calls += 1
            return raw
    client = Fake()
    path, downloaded = save_filing(client, filing, tmp_path)
    assert downloaded and path.name == "NVDA_0001045810-21-000205.html"
    assert save_filing(client, filing, tmp_path) == (path, False)
    assert client.calls == 1
    sections = extract_sections(path.read_bytes(), "10-Q")
    assert sections == extract_sections(path.read_bytes(), "10-Q")
    assert "Revenue improved" in sections["management_discussion"]
    assert "Supply risk" in sections["risk_factors"]
    record = {**filing.__dict__, "sections": sections}
    assert json.loads(json.dumps(record))["source_url"] == filing.source_url


def test_malformed_metadata_and_empty_document(tmp_path):
    with pytest.raises(ValueError):
        parse_filings("NVDA", "0001045810", {"form": []}, {"10-Q"})
    filing = parse_filings("NVDA", "0001045810", table(), {"10-Q"})[0]
    class Empty:
        def get(self, url):
            return b""
    with pytest.raises(ValueError):
        save_filing(Empty(), filing, tmp_path)
    assert not list(tmp_path.iterdir())
    assert extract_sections(b"<html><p>Malformed but readable</p></html>", "10-K") == {
        "management_discussion": "", "risk_factors": ""}


def test_user_agent_required():
    with pytest.raises(ValueError):
        SecClient("anonymous")
    with pytest.raises(ValueError):
        SecClient("FinSight Research your.name@university.edu")
