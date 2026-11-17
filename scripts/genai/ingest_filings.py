"""Bounded point-in-time SEC ingestion: python -m scripts.genai.ingest_filings."""
from __future__ import annotations

import argparse
from datetime import date, datetime, time, timezone
import json
import logging
import os
from pathlib import Path

from src.common.config import load_config
from src.genai.filing_parser import extract_sections
from src.genai.sec_ingestion import SecClient, decision_cutoff, eligible_filings, latest_report_set, save_filing

ROOT = Path(__file__).resolve().parents[2]
LOGGER = logging.getLogger(__name__)


def ingest_one(client: SecClient, filing, root: Path) -> dict:
    cleaned = root / "data/processed/sec_filings" / f"{filing.ticker}_{filing.accession_number}.json"
    if cleaned.exists():
        try:
            previous = json.loads(cleaned.read_text())
            if (previous.get("source_url") == filing.source_url
                    and previous.get("first_eligible_at") == filing.first_eligible_at
                    and isinstance(previous.get("sections"), dict)
                    and (root / previous.get("raw_path", "")).is_file()):
                return previous
        except (OSError, ValueError):
            pass
    raw_path, _ = save_filing(client, filing, root / "data/raw/sec_filings")
    sections = extract_sections(raw_path.read_bytes(), filing.filing_type)
    missing = [name for name, text in sections.items() if not text.strip()]
    record = {**filing.__dict__,
              "availability_basis": "SEC acceptance timestamp; first eligible at next XNYS regular open",
              "retrieved_at": datetime.now(timezone.utc).isoformat(),
              "raw_path": str(raw_path.relative_to(root)),
              "sections": sections,
              "extraction_status": "partial" if missing else "complete",
              "missing_sections": missing}
    cleaned.parent.mkdir(parents=True, exist_ok=True)
    temporary = cleaned.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    temporary.replace(cleaned)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=ROOT / "config/experiment.yaml")
    parser.add_argument("--ticker")
    parser.add_argument("--as-of", type=date.fromisoformat)
    parser.add_argument("--decision-time", type=time.fromisoformat)
    parser.add_argument("--max-downloads", type=int, default=1)
    parser.add_argument("--all-eligible", action="store_true", help="Opt in to all eligible filings")
    parser.add_argument("--dry-run", action="store_true", help="List metadata without downloading")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    config = load_config(args.config)
    pilot, sec = config["pilot"], config["sec"]
    ticker = args.ticker or pilot["vertical_slice_ticker"]
    as_of = args.as_of or date.fromisoformat(str(pilot["decision_date"]))
    decision_time = args.decision_time or time.fromisoformat(str(pilot["decision_time"]))
    start = date.fromisoformat(str(config["experiment"]["start_date"]))
    end = date.fromisoformat(str(config["experiment"]["end_date"]))
    if not start <= as_of <= end:
        parser.error(f"--as-of must be between {start} and {end}")
    if args.max_downloads < 1:
        parser.error("--max-downloads must be positive")
    client = SecClient(os.environ.get("SEC_USER_AGENT", ""), delay=float(sec["request_delay_seconds"]))
    cutoff = decision_cutoff(as_of, decision_time)
    rejections: list[dict] = []
    candidates = eligible_filings(client, ticker, cutoff, set(sec["forms"]), rejections=rejections)
    if rejections and not args.dry_run:
        audit = ROOT / "data/processed/sec_filings" / f"{ticker}_{as_of.isoformat()}_ineligible_metadata.json"
        audit.parent.mkdir(parents=True, exist_ok=True)
        audit.write_text(json.dumps(rejections, indent=2) + "\n")
    selected = candidates if args.all_eligible else latest_report_set(candidates)
    selected = selected[:args.max_downloads]
    if not args.dry_run:
        manifest = ROOT / "data/processed/sec_filings" / f"{ticker}_{as_of.isoformat()}_selection.json"
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({"ticker": ticker, "as_of_date": as_of.isoformat(),
                                        "accessions": [f.accession_number for f in selected]},
                                       indent=2) + "\n")
    print(f"Eligible metadata={len(candidates)} selected={len(selected)} cutoff={cutoff.isoformat()}")
    failed = 0
    for filing in selected:
        if args.dry_run:
            print(f"{filing.ticker} {filing.filing_type} {filing.accession_number} first_eligible={filing.first_eligible_at}")
            continue
        try:
            record = ingest_one(client, filing, ROOT)
            print(f"saved {filing.accession_number} status={record['extraction_status']} missing={record['missing_sections']}")
        except Exception as exc:
            failed += 1
            LOGGER.exception("Failed filing %s", filing.accession_number)
            failures = ROOT / "data/processed/sec_filings/failures.jsonl"
            failures.parent.mkdir(parents=True, exist_ok=True)
            with failures.open("a") as handle:
                handle.write(json.dumps({"ticker": ticker, "accession_number": filing.accession_number,
                                         "source_url": filing.source_url, "error": str(exc),
                                         "recorded_at": datetime.now(timezone.utc).isoformat()}) + "\n")
    print(f"completed={len(selected) - failed} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
