# FinSight: Evaluating Generative AI for Long-Term Equity Selection

**Dean DiCarlo — SEC filings and GenAI; Nicholas Stanis — quantitative data and evaluation.**

Review draft: the original quantitative snapshot has been reproduced by Codex in Nick's workspace; human claim review and a real filing-grounded example remain pending.

## I. Project Overview

Does qualitative financial information extracted by a generative AI model provide measurable value beyond traditional quantitative financial metrics when selecting long-term investments? FinSight studies company ranking rather than exact stock-price prediction. The intended experiment compares passive SPY, quantitative-only selection and selection augmented with filing-derived qualitative signals under matched historical conditions.

Our midpoint work establishes two components: a historical SEC ingestion and retrieval prototype, and a measured price-momentum pilot. It does not yet answer the incremental-value question. The project connects retrieval-augmented generation, prompt design, source grounding and model evaluation with the challenge of preventing future information from entering historical decisions.

## II. Dataset

The executed quantitative pilot uses Yahoo Finance through yfinance 0.2.66 for AAPL, MSFT, NVDA, JPM, XOM and SPY. The saved snapshot contains 518 daily rows per instrument, or 3,108 rows, from December 21, 2020 through January 11, 2023. Local inspection found no duplicate ticker/date rows; saved metadata reports no missing adjusted closes or adjusted opens. Prices exist on the four required ranking and execution boundaries. The snapshot hash and request parameters are recorded in `docs/evidence/yahoo-pilot.md` and the adjacent ignored metadata file.

Historical SEC 10-K and 10-Q filings are the intended qualitative dataset, particularly MD&A and Risk Factors. Live filing coverage and extraction quality have not yet been established by the evidence available for this draft. The broader proposal's Bloomberg, FactSet, FinViz, fundamentals and optional FRED inputs have not been evaluated in this pilot. FactSet access is a later investigation. Data sharing must respect source terms; raw snapshots, credentials and bulk filings are excluded from Git. The fixed stock universe creates selection and survivorship bias.

## III. Methods

At January 3, 2022, 09:30 America/New_York, the quantitative component ranks five stocks by adjusted-close momentum from December 31, 2020 to December 31, 2021. Ties break alphabetically. It selects two stocks with equal weights, enters at the next regular XNYS open on January 4, 2022 and exits at the January 4, 2023 open. Missing or invalid boundary prices cause failure rather than silent date substitution. SPY uses identical execution dates. Forward outcomes are kept separate from ranking inputs.

Adjusted open is calculated as open multiplied by adjusted close divided by close. The ratio of adjusted exit to entry prices approximates total return, but does not establish dividend reinvestment at the open. Returns are gross with zero transaction costs. Independent validation of the dividend-adjusted series is outstanding; verification of a split and split-adjusted close does not resolve that limitation.

The SEC prototype treats a filing as eligible at the first regular market open strictly after acceptance, excludes unknown timestamps and applies the historical decision cutoff. It caches primary HTML, extracts sections heuristically and constructs provenance-bearing chunks. Configuration specifies a 24-month filing lookback, 350-word chunks with 50-word overlap, all-MiniLM-L6-v2 embeddings, local Chroma storage and top-five retrieval. These are configured settings, not evidence that live retrieval has been validated. The current scorer emits a neutral mock value of 0.5 when evidence exists; it is not a real model judgment.

System architecture (rendered as a vector diagram in the PDF):

```text
Yahoo snapshot -> momentum ranking -> top-two portfolio / matched SPY
                                      -> measured forward evaluation
SEC metadata -> eligibility -> HTML/sections -> chunks/index -> retrieval
                                                               -> mock score
Quantitative + real qualitative signals -> joined augmented ranking
                                          -> matched evaluation [PLANNED]
```

The quantitative path has measured outputs; the SEC path is implemented and fixture-tested. A manually sourced case study, if completed, must appear as a separate path. Acceptance-time buffering reduces availability uncertainty but is not proof of first public access. Grounding also cannot eliminate future knowledge in a modern model's pretraining.

## IV. Preliminary Results

| Holding or strategy | Trailing momentum | Forward gross return |
| --- | ---: | ---: |
| NVDA | 125.48% | −51.84% |
| XOM | 57.58% | 69.90% |
| Equal-weight portfolio | — | 9.03% |
| SPY | — | −18.74% |

The portfolio exceeded SPY by 27.77 percentage points; one of two selected stocks outperformed SPY, a 50% hit rate. The opposing holding outcomes show why the portfolio result should not be interpreted as consistent stock-selection success. One cohort and two holdings cannot establish robustness or support a meaningful time-series Sharpe estimate. This is a preliminary momentum comparison, not a quarterly backtest, a fundamentals-based model evaluation or evidence that GenAI improves selection.

Codex independently reran the original CSV in Nick's Windows workspace after transfer of both snapshot and metadata. Its SHA-256 matched the original; all reported holdings and returns reproduced. Inspection confirmed 3,108 rows, zero duplicate ticker/date rows and no missing adjusted opens or closes. With Chroma installed, the merged-source suite returned 16 passed and one skipped (live SEC). A further four-test quantitative run passed in the reproduction PR, including a regression test that changes or removes future observations without changing rankings. These checks do not validate live filing coverage or dividend adjustments. A real filing-grounded LLM example and citation review remain pending; no qualitative result is claimed here.

## V. Next Steps

First, obtain contributor claim review and complete a historically eligible filing case study with exact prompt, source passages, model identity, raw output and citation review. If automated retrieval is blocked, a manually selected example can demonstrate traceability while automated validation remains open. Resolve dividend-adjusted-series verification and record extraction or retrieval failures honestly.

Next, implement real structured scoring with abstention and adequate matched stock coverage. Freeze score combination before evaluation, obtain verified point-in-time fundamentals, and compare SPY, quantitative-only and augmented selection under identical universe, timing, weighting and cost rules. Broader walk-forward evaluation and robustness checks follow the matched pilot; incomplete forward outcomes must be excluded. Fine-tuning and additional data providers remain optional. The final project's central test is incremental value from qualitative signals, which the present momentum results do not measure.
