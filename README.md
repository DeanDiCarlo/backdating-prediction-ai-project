# FinSight — Historical Equity Selection with GenAI

CSE 434/534 project by Dean DiCarlo and Nicholas Stanis.

## Research question
Does qualitative information extracted from historical SEC filings using GenAI provide measurable incremental value beyond a quantitative financial model when selecting stocks likely to outperform SPY?

## Experimental comparison
1. SPY buy-and-hold reference.
2. Quantitative-only ranking.
3. Quantitative + GenAI filing-signal ranking.

All features must be available **on or before the decision date**. Never use current filings to score historical dates.

## Workstreams
- **Nick (quantitative):** historical prices, point-in-time fundamentals, labels, baseline ranker, SPY and portfolio evaluation. Work in `src/quant/`, `scripts/quant/`, and related tests.
- **Dean (GenAI):** SEC filing ingestion, historical availability filters, retrieval, grounded scoring, citations, and structured outputs. Work in `src/genai/`, `scripts/genai/`, and related tests.
- **Shared:** `src/common/`, schemas, methodology, report, integration; changes require agreement.

## Initial data contract
One row per `ticker` and `as_of_date` (ISO YYYY-MM-DD) with:
- Quant: `ticker, as_of_date, quant_score` (optionally feature columns and `feature_available_at`).
- GenAI: `ticker, as_of_date, qualitative_score, filing_accession, filing_date, filing_available_at, evidence`.
- Joined: `ticker, as_of_date, quant_score, qualitative_score`; scoring combination is defined in one shared experiment config.
- Evaluation: `ticker, as_of_date, forward_total_return, spy_forward_total_return, excess_forward_return` (not inputs to either ranker).

**Do not train on future labels or data**. Store provenance (source, publish/acceptance date, retrieval time, filing accession). Reconstruct historical universe membership when possible; if using today's constituents, report survivorship bias as a limitation.

## Suggested first milestone
Use a small fixed universe (e.g., 5–10 stocks), one historical decision date, and an explicitly specified forward horizon. First run the quant baseline and 1–2 evidence-grounded filing scores. Then integrate on the shared keys and expand to walk-forward evaluation.

## Repo workflow
- `main` is the stable integration branch.
- `feature/quant-baseline` (Nick); `feature/genai-filings` (Dean).
- One pull request per workstream; avoid editing the same files.
- Commit reproducible scripts, dependency/config instructions, small sanitized samples, tests and report figures; do not commit API keys, licensed Bloomberg/FactSet data, or bulk downloaded filings.

## Midterm report checklist
2–3 pages, 11-point single-column type, 1-inch margins; team and roles at top. Sections: I. Project Overview; II. Dataset; III. Methods + architecture diagram; IV. Preliminary Results; V. Next Steps. Never claim results that were not actually measured.
