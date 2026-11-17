"""Audit cached NVDA extraction and real retrieval; outputs stay Git ignored."""
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path

from scripts.genai.ingest_filings import ROOT, ingest_one
from src.genai.chunking import chunk_document
from src.genai.filing_parser import readable_text
from src.genai.retrieval import FilingIndex, LocalEmbedder
from src.genai.sec_ingestion import Filing


def main():
    accession = '0001045810-21-000010'
    path = ROOT / f'data/processed/sec_filings/NVDA_{accession}.json'
    record = json.loads(path.read_text())
    raw = ROOT / record['raw_path']
    source = readable_text(raw.read_bytes())
    assert all(s and s in source for s in record['sections'].values())
    # Verify cached ingestion needs no document request.
    class NoNetwork:
        def get(self, url):
            raise AssertionError('Cache reuse attempted a download')
    filing = Filing(**{k: record[k] for k in Filing.__dataclass_fields__})
    assert ingest_one(NoNetwork(), filing, ROOT) == record
    chunks = chunk_document(record, chunk_words=350, overlap_words=50)
    model = 'sentence-transformers/all-MiniLM-L6-v2'
    embedder = LocalEmbedder(model)
    index_path = ROOT / 'data/chroma_db/live_validation'
    index = FilingIndex(index_path, embedder, model_id=model)
    index.upsert(chunks)
    reopened = FilingIndex(index_path, embedder, model_id=model)
    assert reopened.collection.count() == len(chunks)
    cutoff = datetime.fromisoformat('2022-01-03T09:30:00-05:00')
    query = 'growth competitive position and business risks'
    args = dict(ticker='NVDA', cutoff=cutoff, top_k=5, lookback_months=24)
    passages = reopened.search(query, **args)
    assert len(passages) == 5
    assert all(p['metadata']['accession_number'] == accession for p in passages)
    assert all(datetime.fromisoformat(p['metadata']['first_eligible_at']) <= cutoff for p in passages)
    assert all(p['text'] in ' '.join(record['sections'][p['metadata']['section']].split()) for p in passages)
    checks = {
        'wrong_ticker': len(reopened.search(query, **{**args, 'ticker': 'MSFT'})),
        'before_eligibility': len(reopened.search(query, **{**args, 'cutoff': datetime.fromisoformat('2021-02-26T09:30:00-05:00')})),
        'stale_one_month_lookback': len(reopened.search(query, **{**args, 'lookback_months': 1})),
    }
    assert all(n == 0 for n in checks.values())
    output = ROOT / 'outputs/genai/live-validation'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'passages.json').write_text(json.dumps(passages, indent=2))
    revision = getattr(embedder.model[0].auto_model.config, '_commit_hash', None)
    ref = Path(os.environ.get('HF_HOME', str(Path.home() / '.cache/huggingface'))) / 'hub/models--sentence-transformers--all-MiniLM-L6-v2/refs/main'
    if revision is None and ref.is_file():
        revision = ref.read_text().strip()
    audit = {
        'run_at_utc': datetime.now(timezone.utc).isoformat(),
        'source_url': record['source_url'], 'accession': accession,
        'accepted_at': record['filing_available_at'], 'eligible_at': record['first_eligible_at'],
        'raw_sha256': hashlib.sha256(raw.read_bytes()).hexdigest(),
        'raw_bytes': raw.stat().st_size, 'cache_reuse_without_network': True,
        'section_words': {k: len(v.split()) for k, v in record['sections'].items()},
        'chunk_count': len(chunks), 'reopened_count': reopened.collection.count(),
        'chunks_by_section': {s: sum(c['section'] == s for c in chunks) for s in record['sections']},
        'query': query, 'model': model, 'retrieved_count': len(passages),
        'model_revision': revision,
        'retrieved_source_matches': len(passages),
        'versions': {name: version(name) for name in ['sentence-transformers', 'transformers', 'torch', 'chromadb']},
        'exclusion_counts': checks,
    }
    (output / 'audit.json').write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
