"""Deterministic mock scoring for pipeline validation, not investment inference."""
from __future__ import annotations

from datetime import date

from src.common.schemas import QualFeature

FACTORS = ("growth_outlook", "competitive_position", "financial_strength",
           "management_outlook", "business_risks", "strategic_execution")


def mock_score(ticker: str, as_of_date: date, passages: list[dict], *, top_k: int) -> QualFeature:
    evidence = tuple({"accession_number": p["metadata"]["accession_number"],
                      "section": p["metadata"]["section"],
                      "source_url": p["metadata"]["source_url"],
                      "first_eligible_at": p["metadata"].get("first_eligible_at"),
                      "excerpt": p["text"][:240]} for p in passages)
    return QualFeature(
        ticker=ticker.upper(), as_of_date=as_of_date,
        qualitative_score=0.5 if evidence else None,
        filing_accessions=tuple(sorted({e["accession_number"] for e in evidence})),
        evidence=evidence,
        metadata={"provider": "deterministic_mock", "model_id": "neutral-v1",
                  "prompt_version": "mock-v1", "retrieval_top_k": top_k,
                  "factor_scores": {factor: 0.5 for factor in FACTORS},
                  "missing_evidence": not bool(evidence),
                  "status": "mock_only" if evidence else "abstained",
                  "explanation": "Neutral placeholder; no predictive claim."},
    )
