"""Point-in-time SEC EDGAR metadata, download, and provenance handling."""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta, timezone
import json
import logging
import os
from pathlib import Path
import re
import time as clock
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from src.common.dates import exchange_session_open

SEC_TZ = ZoneInfo("America/New_York")
SEC_BASE = "https://www.sec.gov"
DATA_BASE = "https://data.sec.gov"
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Filing:
    ticker: str
    cik: str
    accession_number: str
    filing_type: str
    filing_date: str
    filing_available_at: str
    source_url: str
    first_eligible_at: str | None = None


def decision_cutoff(as_of: date, at: time = time(9, 30)) -> datetime:
    """Default decision is market open in New York on the given date."""
    return datetime.combine(as_of, at, SEC_TZ)


def is_available(available_at: str | None, cutoff: datetime) -> bool:
    """Unknown/naive timestamps are ineligible; cutoff is strictly exclusive."""
    if not available_at or cutoff.tzinfo is None:
        return False
    try:
        value = datetime.fromisoformat(available_at)
    except (TypeError, ValueError):
        return False
    return value.tzinfo is not None and value < cutoff


def acceptance_timestamp(value: str | None) -> str | None:
    """SEC submissions acceptanceDateTime is Eastern wall time when offset absent."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        # During the autumn clock change, a local wall time can mean two instants.
        if parsed.replace(tzinfo=SEC_TZ, fold=0).utcoffset() != parsed.replace(tzinfo=SEC_TZ, fold=1).utcoffset():
            return None
        parsed = parsed.replace(tzinfo=SEC_TZ)
    return parsed.isoformat()


def first_eligible_open(accepted_at: str, session_open: Callable[[date], datetime | None] = exchange_session_open) -> str:
    """First regular market open strictly after SEC acceptance."""
    accepted = datetime.fromisoformat(accepted_at)
    if accepted.tzinfo is None:
        raise ValueError("Acceptance timestamp must be timezone aware")
    local_date = accepted.astimezone(SEC_TZ).date()
    for offset in range(15):
        opening = session_open(local_date + timedelta(days=offset))
        if opening is not None:
            if opening.tzinfo is None:
                raise ValueError("Session open must be timezone aware")
            if opening > accepted:
                return opening.astimezone(timezone.utc).isoformat()
    raise ValueError("No market session found within 15 days of acceptance")


class SecClient:
    def __init__(self, user_agent: str, *, delay: float = 0.2,
                 opener: Callable = urlopen, sleep: Callable = clock.sleep):
        if not user_agent.strip() or "@" not in user_agent or "your.name@" in user_agent:
            raise ValueError("SEC_USER_AGENT must identify the application and contact email")
        self.user_agent, self.delay, self.opener, self.sleep = user_agent, delay, opener, sleep
        self._last_request = 0.0

    def get(self, url: str) -> bytes:
        if not url.startswith((SEC_BASE + "/", DATA_BASE + "/")):
            raise ValueError("Unexpected SEC URL")
        for attempt in range(4):
            elapsed = clock.monotonic() - self._last_request
            if elapsed < self.delay:
                self.sleep(self.delay - elapsed)
            self._last_request = clock.monotonic()
            request = Request(url, headers={"User-Agent": self.user_agent,
                                            "Accept-Encoding": "identity"})
            try:
                with self.opener(request, timeout=30) as response:
                    return response.read()
            except HTTPError as exc:
                if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    raise
            except URLError:
                if attempt == 3:
                    raise
            self.sleep(2 ** attempt)
        raise RuntimeError("SEC request failed")

    def get_json(self, url: str) -> dict:
        data = json.loads(self.get(url))
        if not isinstance(data, dict):
            raise ValueError("Expected SEC JSON object")
        return data


def resolve_cik(ticker: str, mapping: dict) -> str:
    for row in mapping.values():
        if isinstance(row, dict) and str(row.get("ticker", "")).upper() == ticker.upper():
            return f'{int(row["cik_str"]):010d}'
    raise KeyError(f"Ticker not found in SEC map: {ticker}")


def parse_filings(ticker: str, cik: str, table: dict, forms: set[str],
                  rejections: list[dict] | None = None) -> list[Filing]:
    required = ("accessionNumber", "form", "filingDate", "acceptanceDateTime", "primaryDocument")
    if any(not isinstance(table.get(k), list) for k in required):
        raise ValueError("Malformed SEC submissions table")
    length = len(table["accessionNumber"])
    if any(len(table[k]) != length for k in required):
        raise ValueError("Inconsistent SEC submissions columns")
    result = []
    for i in range(length):
        form = table["form"][i]
        if form not in forms:
            continue
        accession = table["accessionNumber"][i]
        document = table["primaryDocument"][i]
        available = acceptance_timestamp(table["acceptanceDateTime"][i])
        def reject(reason: str) -> None:
            if rejections is not None:
                rejections.append({"ticker": ticker.upper(), "accession_number": str(accession),
                                   "reason": reason})
        try:
            date.fromisoformat(table["filingDate"][i])
        except (TypeError, ValueError):
            reject("invalid_filing_date")
            continue
        if not available:
            reject("unknown_or_ambiguous_acceptance_time")
            continue
        if not re.fullmatch(r"\d{10}-\d{2}-\d{6}", str(accession)):
            reject("invalid_accession_number")
            continue
        if not isinstance(document, str) or not document or "/" in document or ".." in document:
            reject("invalid_primary_document")
            continue
        url = f"{SEC_BASE}/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/{document}"
        result.append(Filing(ticker.upper(), cik, accession, form,
                             table["filingDate"][i], available, url))
    return result


def eligible_filings(client: SecClient, ticker: str, cutoff: datetime,
                     forms: set[str], *,
                     session_open: Callable[[date], datetime | None] = exchange_session_open,
                     rejections: list[dict] | None = None) -> list[Filing]:
    mapping = client.get_json(f"{SEC_BASE}/files/company_tickers.json")
    cik = resolve_cik(ticker, mapping)
    submissions = client.get_json(f"{DATA_BASE}/submissions/CIK{cik}.json")
    tables = [submissions.get("filings", {}).get("recent", {})]
    for item in submissions.get("filings", {}).get("files", []):
        # Older submissions are required for historical reproducibility.
        if item.get("filingFrom") and item["filingFrom"] >= cutoff.date().isoformat():
            continue
        name = item.get("name", "")
        if re.fullmatch(r"CIK\d+-submissions-\d+\.json", name):
            try:
                tables.append(client.get_json(f"{DATA_BASE}/submissions/{name}"))
            except (HTTPError, URLError, ValueError) as exc:
                LOGGER.warning("Could not load SEC submissions archive %s: %s", name, exc)
    filings = []
    for table in tables:
        try:
            parsed = parse_filings(ticker, cik, table, forms, rejections)
        except ValueError as exc:
            LOGGER.warning("Skipping malformed submissions table for %s: %s", ticker, exc)
            continue
        for filing in parsed:
            try:
                eligible_at = first_eligible_open(filing.filing_available_at, session_open)
            except ValueError:
                if rejections is not None:
                    rejections.append({"ticker": ticker.upper(), "accession_number": filing.accession_number,
                                       "reason": "unknown_market_eligibility"})
                continue
            if is_available(eligible_at, cutoff) or datetime.fromisoformat(eligible_at) == cutoff:
                filings.append(replace(filing, first_eligible_at=eligible_at))
    return sorted({f.accession_number: f for f in filings}.values(),
                  key=lambda f: (f.filing_available_at, f.accession_number))


def latest_report_set(filings: list[Filing]) -> list[Filing]:
    """Latest eligible 10-K plus later eligible 10-Q filings."""
    annual = [f for f in filings if f.filing_type == "10-K"]
    if not annual:
        return []
    latest = max(annual, key=lambda f: (f.filing_available_at, f.accession_number))
    quarterly = [f for f in filings if f.filing_type == "10-Q"
                 and f.filing_available_at > latest.filing_available_at]
    return [latest, *sorted(quarterly, key=lambda f: f.filing_available_at)]


def save_filing(client: SecClient, filing: Filing, root: Path) -> tuple[Path, bool]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{filing.ticker}_{filing.accession_number}.html"
    if path.exists() and path.stat().st_size:
        return path, False
    data = client.get(filing.source_url)
    if not data.strip():
        raise ValueError(f"Empty filing: {filing.source_url}")
    temp = path.with_suffix(".tmp")
    temp.write_bytes(data)
    temp.replace(path)
    return path, True
