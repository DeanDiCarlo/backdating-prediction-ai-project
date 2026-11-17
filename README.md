# FinSight — Historical Equity Selection with GenAI

CSE 434/534 project by Dean DiCarlo and Nicholas Stanis.

## Research question
Does qualitative information extracted from historical SEC filings using GenAI provide measurable incremental value beyond a quantitative financial model when selecting stocks likely to outperform SPY?

## Experimental comparison
1. SPY buy-and-hold reference.
2. Quantitative-only ranking.
3. Quantitative + GenAI filing-signal ranking.

All features must be available **on or before the decision date**. Never use current filings to score historical dates.

## Team collaboration
Dean DiCarlo and Nicholas Stanis share responsibility for data quality, historical availability, GenAI design, model evaluation, financial validation, and reporting. Both review the integrated experiment and its claims. Coordinate task leads as work progresses and cross-review changes across the quantitative and GenAI components.

## Data flow

`SEC submissions metadata → eligibility calculation → cached primary HTML → normalized section JSON → deterministic chunks → local Chroma index → cutoff-filtered passages → mock qualitative record`. Raw HTML, normalized JSON, selection manifests, Chroma files, and mock outputs stay in Git-ignored directories. The future quantitative provider joins through `(ticker, as_of_date)` records in `src/common/schemas.py`; no FactSet format is assumed or stored here.

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
- Use focused feature branches for quantitative and GenAI changes; either contributor can work across components.
- Use focused pull requests and coordinate edits; review integration and experimental assumptions together.
- Commit reproducible scripts, dependency/config instructions, small sanitized samples, tests and report figures; do not commit API keys, licensed Bloomberg/FactSet data, or bulk downloaded filings.

## Midterm report checklist
2–3 pages, 11-point single-column type, 1-inch margins; team and roles at top. Sections: I. Project Overview; II. Dataset; III. Methods + architecture diagram; IV. Preliminary Results; V. Next Steps. Never claim results that were not actually measured.


## Historical SEC ingestion

Use Python 3.11 or newer. Create a virtual environment and install the package and tests:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Set `SEC_USER_AGENT` to a descriptive application name and your working contact email (see `.env.example`). The command does not load `.env` automatically. The checked-in example is a placeholder and must be replaced for live SEC requests.

```bash
export SEC_USER_AGENT='FinSight Research your.actual.email@example.edu'
python -m scripts.genai.ingest_filings --dry-run
python -m scripts.genai.ingest_filings
pytest -q
```

The pilot decision is **2022-01-03 at 09:30 America/New_York** by default. Override with `--ticker`, `--as-of`, or `--decision-time HH:MM:SS` if needed. A filing becomes eligible at the first regular XNYS open strictly after SEC acceptance, and its first eligible time must be on or before the decision cutoff. SEC submissions timestamps without offsets are interpreted as New York local time. Unknown or malformed timestamps are excluded. Simulated execution uses the next regular open strictly after the decision cutoff.

SEC acceptance is a proxy for first public availability; the next-open buffer reduces but does not eliminate uncertainty. Studies needing a stronger point-in-time guarantee should independently archive first-seen times. Ambiguous local times during the autumn clock change are excluded.

Raw primary documents are cached under `data/raw/sec_filings/`; processed JSON is under `data/processed/sec_filings/`, both named `{ticker}_{accession}`. Both directories are Git ignored. The JSON records source URL, accession, filing and acceptance dates, first eligible time, retrieval time, raw path, extracted sections, and missing-section status. A selection manifest, ineligible-metadata audit, and failure log are stored beside the processed JSON. The default command downloads at most one filing from the latest eligible 10-K plus subsequent 10-Q set. Use `--max-downloads 4` to cover more of that set; `--all-eligible` must be explicit. SEC requests are throttled to at most five per second per process and retried on transient errors. Older submissions index files are consulted where listed.

HTML section extraction is heuristic: heading styles, tables of contents, inline XBRL, and non-HTML documents can cause missing or imperfect MD&A/Risk Factors text. Review extracted evidence before scoring. A failed filing is logged and does not stop the rest of a bounded batch.

For the local retrieval and mock-scoring slice, install the optional retrieval dependencies and run:

```bash
python -m pip install -e '.[retrieval]'
python -m scripts.genai.run_vertical_slice --max-downloads 1
```

This chunks only the selected manifest, persists Chroma under `data/chroma_db/`, filters on ticker, configured feature lookback, and first eligible time before similarity ranking, and writes a **neutral mock** result under `outputs/genai/`. The mock score is a pipeline demonstration, not a financial result. A local sentence-transformer model download is required on first run. The config records the 2016-01-01 to 2026-11-16 research window, daily price frequency, quarterly decisions, and 12-month target. The forward outcome is complete only when prices through the first trading session on or after the 12-month horizon from execution are observed; the single-cohort Yahoo pilot implements matched forward returns, while broader walk-forward evaluation remains planned. Modern LLMs may contain future information from pretraining, so evidence grounding alone will not eliminate leakage in later real-provider experiments.

Real SEC metadata is tested separately and only when both `RUN_SEC_INTEGRATION=1` and a real `SEC_USER_AGENT` are set. Run `pytest -m integration` after configuring them. The default test run uses mocked network responses.

**Current verification (2026-11-17 UTC):** all 18 tests passed with live SEC enabled in Nick's workspace. The original Yahoo snapshot reproduced with a matching hash. One real eligible NVDA 10-K yielded 56 chunks; real MiniLM/Chroma retrieval and cutoff, ticker and stale-lookback exclusions passed. See [live evidence](docs/evidence/live-nvda.md) and the [manual grounded example](docs/evidence/manual-nvda-case.md). The example abstains from investment scoring and has agent self-review only. Dividend-adjustment verification and final human claim review remain open; no incremental GenAI investment value is established.

## Original midpoint draft

The earlier draft and handoff are retained for provenance. Start with issue #3 and [the ordered execution handoff](docs/midpoint-handoff.md). The [report source](docs/midterm-draft.md), [three-page review PDF](docs/midterm-report.pdf) and [build instructions](docs/report-build.md) retain the measured evidence and its limitations. [Readiness](docs/midpoint-readiness.md) records the exact review artifact and outstanding contributor review. Submission is recorded separately and has not occurred.

## Revised midpoint check-in

See [the new source](docs/midpoint-checkin.md), [review PDF](docs/midpoint-checkin.pdf), [claim review ledger](docs/midpoint-review-ledger.md), and [remaining-project handoff](docs/final-project-handoff.md). The new experiment is specified but unexecuted because its preserved filing cache is unavailable here. Contributor review remains pending.
