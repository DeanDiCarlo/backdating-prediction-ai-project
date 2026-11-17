"""Run bounded NVDA ingestion, local retrieval, and mock scoring."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date
import json
from pathlib import Path

from scripts.genai.ingest_filings import ROOT, main as ingest_main
from src.common.config import load_config
from src.genai.chunking import chunk_document
from src.genai.retrieval import FilingIndex, LocalEmbedder
from src.genai.scoring import mock_score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/experiment.yaml")
    parser.add_argument("--max-downloads", type=int, default=1)
    args = parser.parse_args(argv)
    config = load_config(args.config)
    ticker = config["pilot"]["vertical_slice_ticker"]
    decision = date.fromisoformat(str(config["pilot"]["decision_date"]))
    status = ingest_main(["--config", str(args.config), "--ticker", ticker,
                          "--max-downloads", str(args.max_downloads)])
    if status:
        return status
    store = ROOT / "data/processed/sec_filings"
    manifest = json.loads((store / f"{ticker}_{decision.isoformat()}_selection.json").read_text())
    records = [store / f"{ticker}_{accession}.json" for accession in manifest["accessions"]]
    if not records or not all(path.exists() for path in records):
        raise RuntimeError("No normalized filing was saved")
    chosen = [json.loads(path.read_text()) for path in records]
    retrieval = config["retrieval"]
    chunks = [chunk for record in chosen for chunk in
              chunk_document(record, chunk_words=int(retrieval["chunk_words"]),
                             overlap_words=int(retrieval["overlap_words"]))]
    if not chunks:
        raise RuntimeError("No narrative chunks could be extracted")
    index = FilingIndex(ROOT / "data/chroma_db", LocalEmbedder(retrieval["embedding_model"]),
                        model_id=retrieval["embedding_model"])
    index.upsert(chunks)
    from src.genai.sec_ingestion import decision_cutoff
    from datetime import time
    cutoff = decision_cutoff(decision, time.fromisoformat(str(config["pilot"]["decision_time"])))
    top_k = int(retrieval["top_k"])
    passages = index.search("growth competitive position and business risks",
                            ticker=ticker, cutoff=cutoff, top_k=top_k,
                            lookback_months=int(config["experiment"]["feature_lookback_months"]))
    result = mock_score(ticker, decision, passages, top_k=top_k)
    output = ROOT / "outputs/genai" / f"{ticker}_{decision.isoformat()}_mock.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(result), default=str, indent=2, sort_keys=True) + "\n")
    print(f"chunks={len(chunks)} retrieved={len(passages)} mock_result={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
