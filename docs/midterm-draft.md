# FinSight: Evaluating Generative AI for Long-Term Equity Selection

**Dean DiCarlo — SEC filings and GenAI; Nicholas Stanis — quantitative data and evaluation.**

Review draft: quantitative reproduction, live filing retrieval and a manual grounded example are complete; final contributor claim review remains pending.

## I. Project Overview

Does qualitative financial information extracted by a generative AI model provide measurable value beyond traditional quantitative financial metrics when selecting long-term investments? FinSight studies company ranking rather than exact stock-price prediction. The intended experiment compares passive SPY, quantitative-only selection and selection augmented with filing-derived qualitative signals under matched historical conditions.

Our midpoint work establishes two components: a historical SEC ingestion and retrieval prototype, and a measured price-momentum pilot. It does not yet answer the incremental-value question. The project connects retrieval-augmented generation, prompt design, source grounding and model evaluation with the challenge of preventing future information from entering historical decisions.

## II. Dataset

The executed quantitative pilot uses Yahoo Finance through yfinance 0.2.66 for AAPL, MSFT, NVDA, JPM, XOM and SPY. The saved snapshot contains 518 daily rows per instrument, or 3,108 rows, from December 21, 2020 through January 11, 2023. Local inspection found no duplicate ticker/date rows; saved metadata reports no missing adjusted closes or adjusted opens. Prices exist on the four required ranking and execution boundaries. The snapshot hash and request parameters are recorded in `docs/evidence/yahoo-pilot.md` and the adjacent ignored metadata file.

The qualitative pilot retrieved one real NVDA fiscal 2021 10-K (accession 0001045810-21-000010). It was accepted February 26, 2021 at 22:03:14 UTC and first eligible March 1 at 14:30 UTC. MD&A contains 6,346 words and Risk Factors 10,313 words, producing 21 and 35 chunks respectively. The annual filing is only part of the information available by the cutoff; subsequent quarters were not downloaded. Source hashes and timestamps are retained in the evidence notes. Spot checks found retained page markers and concatenated financial-table cells. The proposal's fundamentals and other providers remain unevaluated. Raw snapshots, credentials and bulk filings are excluded from Git; sharing must respect source terms. The fixed stock universe creates selection and survivorship bias.

## III. Methods

At January 3, 2022, 09:30 America/New_York, the quantitative component ranks five stocks by adjusted-close momentum from December 31, 2020 to December 31, 2021. Ties break alphabetically. It selects two stocks with equal weights, enters at the next regular XNYS open on January 4, 2022 and exits at the January 4, 2023 open. Missing or invalid boundary prices cause failure rather than silent date substitution. SPY uses identical execution dates. Forward outcomes are kept separate from ranking inputs.

Adjusted open is calculated as open multiplied by adjusted close divided by close. The ratio of adjusted exit to entry prices approximates total return, but does not establish dividend reinvestment at the open. Returns are gross with zero transaction costs. Independent validation of the dividend-adjusted series is outstanding; verification of a split and split-adjusted close does not resolve that limitation.

The SEC component treats a filing as eligible at the first regular market open strictly after acceptance, excludes unknown timestamps and applies the historical cutoff. It caches primary HTML, extracts sections heuristically and creates 350-word chunks with 50-word overlap. We executed all-MiniLM-L6-v2 embeddings and persisted 56 chunks in Chroma. Reopening the index preserved all records. The query “growth competitive position and business risks” retrieved five source-matched passages under a 24-month lookback. The production scorer still emits a neutral mock 0.5; that value is not a model finding.

Separately, a manual in-session Codex run used three exact excerpts from the eligible filing. The prompt restricted observations to those excerpts, required evidence IDs and instructed abstention without a calibrated basis for an outperformance score. Exact prompt, response, model identity limitations and source checks are retained. This example used manually selected text, not similarity-ranked passages. Codex checked its own citations; human review is pending. The authoring session knew later pilot returns, so this is not blinded predictive evaluation.

System architecture (rendered as a vector diagram in the PDF):

```text
Yahoo snapshot -> momentum ranking -> top-two portfolio / matched SPY
                                      -> measured forward evaluation
SEC metadata -> eligibility -> HTML/sections -> chunks/index -> retrieval
                                                               -> five passages
Manual eligible excerpts -> recorded Codex response / abstention
Quantitative + real qualitative signals -> joined augmented ranking
                                          -> matched evaluation [PLANNED]
```

The quantitative and retrieval paths have measured outputs; augmented investment ranking remains planned. Acceptance buffering reduces availability uncertainty but does not prove first public access. Source grounding cannot eliminate future knowledge in a modern model's pretraining.

## IV. Preliminary Results

| Holding or strategy | Trailing momentum | Forward gross return |
| --- | ---: | ---: |
| NVDA | 125.48% | −51.84% |
| XOM | 57.58% | 69.90% |
| Equal-weight portfolio | — | 9.03% |
| SPY | — | −18.74% |

The portfolio exceeded SPY by 27.77 percentage points; one of two selected stocks outperformed SPY, a 50% hit rate. The opposing holding outcomes show why the portfolio result should not be interpreted as consistent stock-selection success. One cohort and two holdings cannot establish robustness or support a meaningful time-series Sharpe estimate. This is a preliminary momentum comparison, not a quarterly backtest, a fundamentals-based model evaluation or evidence that GenAI improves selection.

Codex reproduced the original snapshot in Nick's workspace with the matching SHA-256 and identical holdings/returns. All 18 tests passed with live SEC enabled, including a regression check that changing or deleting future observations cannot change historical rankings. Four pandas deprecation warnings remain. Real retrieval returned zero passages for a wrong ticker, a pre-eligibility cutoff and a stale one-month lookback. All five retrieved passages came from Risk Factors, showing that this query does not establish balanced growth/risk coverage or retrieval accuracy.

The manual model example described reported fiscal 2021 segment revenue growth (Graphics 29%; Compute & Networking 109%) and third-party manufacturing control risk. All three cited excerpts matched the source; agent self-review found two supported observations and zero unsupported observations. The response abstained from assigning an outperformance score and from inferring valuation or future returns. These descriptive counts for one selected example are not an accuracy estimate or independent review. The model output demonstrates traceability and abstention, not GenAI investment value. Human claim review remains pending.

Reproduction commands, hashes, exact prompt/response and source provenance are retained under `docs/evidence/` in the repository, particularly `nick-reproduction.md`, `live-nvda.md` and `manual-nvda-case.md`. Raw data and model caches remain local.

## V. Next Steps

First, complete contributor claim review, independently verify dividend adjustments and improve extraction/table cleanup. Test query and section coverage using reviewed relevance judgments. Run a separate blinded provider experiment with recorded model revision, prompts and abstentions; the current manual example cannot establish investment performance.

Next, implement real structured scoring with abstention and adequate matched stock coverage. Freeze score combination before evaluation, obtain verified point-in-time fundamentals, and compare SPY, quantitative-only and augmented selection under identical universe, timing, weighting and cost rules. Broader walk-forward evaluation and robustness checks follow the matched pilot; incomplete forward outcomes must be excluded. Fine-tuning and additional data providers remain optional. The final project's central test is incremental value from qualitative signals, which the present momentum results do not measure.
