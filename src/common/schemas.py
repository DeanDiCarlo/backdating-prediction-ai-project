"""Provider-independent feature contract for future quantitative integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite


def _score(value: float) -> None:
    if not isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Normalized scores must be finite and in [0, 1]")


@dataclass(frozen=True)
class QuantFeature:
    ticker: str
    as_of_date: date
    quant_score: float
    feature_available_at: datetime
    metadata: dict

    def __post_init__(self):
        _score(self.quant_score)
        if self.feature_available_at.tzinfo is None:
            raise ValueError("Quant feature availability must be timezone aware")


@dataclass(frozen=True)
class QualFeature:
    ticker: str
    as_of_date: date
    qualitative_score: float | None
    filing_accessions: tuple[str, ...]
    evidence: tuple[dict, ...]
    metadata: dict

    def __post_init__(self):
        if self.qualitative_score is not None:
            _score(self.qualitative_score)
            if not self.evidence:
                raise ValueError("Scored qualitative features require evidence")


def join_features(quant: QuantFeature, qualitative: QualFeature, decision_cutoff: datetime) -> dict:
    if (quant.ticker, quant.as_of_date) != (qualitative.ticker, qualitative.as_of_date):
        raise ValueError("Feature keys differ")
    if decision_cutoff.tzinfo is None or quant.feature_available_at > decision_cutoff:
        raise ValueError("Quant feature was not available by the decision cutoff")
    for item in qualitative.evidence:
        available = item.get("first_eligible_at")
        if not available:
            raise ValueError("Qualitative evidence has no eligibility timestamp")
        timestamp = datetime.fromisoformat(available)
        if timestamp.tzinfo is None or timestamp > decision_cutoff:
            raise ValueError("Qualitative evidence was not eligible by the decision cutoff")
    return {"ticker": quant.ticker, "as_of_date": quant.as_of_date.isoformat(),
            "quant_score": quant.quant_score, "qualitative_score": qualitative.qualitative_score}
