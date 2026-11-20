"""Deterministic word chunks with filing provenance."""
from __future__ import annotations

from datetime import datetime
import hashlib


def chunk_document(record: dict, *, chunk_words: int, overlap_words: int) -> list[dict]:
    if chunk_words <= 0 or not 0 <= overlap_words < chunk_words:
        raise ValueError("Invalid chunk size or overlap")
    available = record.get("first_eligible_at")
    if not available or datetime.fromisoformat(available).tzinfo is None:
        raise ValueError("Filing has no verified eligibility timestamp")
    chunks = []
    for section, content in record["sections"].items():
        words = content.split()
        step = chunk_words - overlap_words
        for index, start in enumerate(range(0, len(words), step)):
            text = " ".join(words[start:start + chunk_words])
            seed = f"{record['accession_number']}|{section}|{index}|{text}"
            chunks.append({
                "id": hashlib.sha256(seed.encode()).hexdigest(),
                "text": text,
                "ticker": record["ticker"],
                "accession_number": record["accession_number"],
                "section": section,
                "filing_date": record["filing_date"],
                "source_url": record["source_url"],
                "first_eligible_at": available,
                "first_eligible_epoch": int(datetime.fromisoformat(available).timestamp()),
            })
            if start + chunk_words >= len(words):
                break
    return chunks
