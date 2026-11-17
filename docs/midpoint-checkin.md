# FinSight: Historical Equity Selection with GenAI

CSE 434/534 | Midpoint Check-In | November 17, 2026

**Dean DiCarlo and Nicholas Stanis:** shared development and review across data, GenAI, and evaluation.

## I. Project Overview

Can information extracted from historical corporate filings improve stock selection beyond a quantitative baseline? FinSight compares SPY, quantitative-only selection, and selection augmented with filing-derived signals. Investors already use financial statements and business narratives together. Our research asks whether a generative model can make the narrative component systematic, traceable, and useful under matched historical conditions.

At midpoint, we have a reproducible momentum pilot and an operational historical filing retrieval pipeline. The two components are not yet integrated into an investment experiment. This checkpoint connects course topics in retrieval-augmented generation, prompt design, grounding, and evaluation. Our main lesson is that reliable evidence availability and meaningful evaluation must precede a more elaborate model.

## II. Dataset

The price pilot uses Yahoo Finance through yfinance 0.2.66: five stocks (AAPL, MSFT, NVDA, JPM, XOM) plus SPY. The saved snapshot contains 3,108 daily rows, 518 per instrument, from December 21, 2020 through January 11, 2023. Recorded checks found no duplicate ticker/date rows or missing adjusted boundary prices. The original snapshot was reproduced in the second contributor's workspace [1]. The fixed universe is a development sample, not a representative investment universe. Its selection rationale remains to be documented.

FactSet access proved difficult for this checkpoint. Nicholas is investigating escalation and whether additional data can be obtained. We therefore used an accessible price snapshot and public SEC filings to validate the workflow. Fundamentals and the broader provider coverage in our proposal remain future work. This scope reduction establishes a testable baseline while access is unresolved.

The text pilot contains one NVDA fiscal 2021 10-K, accession 0001045810-21-000010 [2]. It yielded 6,346 MD&A words and 10,313 Risk Factors words, split into 56 chunks. Extraction retains some page markers and concatenated table cells. Subsequent quarterly filings were not downloaded, so this is incomplete evidence at the decision date. Source terms govern sharing; private snapshots and bulk filings remain outside Git. Fixed-universe selection bias and pretrained model knowledge also constrain interpretation.

**Next evidence checkpoint.** A six-question evaluation covering growth, acquisition context, manufacturing, competition, liquidity, and abstention is specified but unexecuted: the preserved filing cache is absent here. The next run will assess passage relevance and answer support separately, retaining failures.

## III. Methods

At January 3, 2022, 09:30 New York time, the baseline ranks the five stocks by adjusted-close return from December 31, 2020 to December 31, 2021. It selects two with equal weights, enters at the January 4, 2022 open, and exits at the January 4, 2023 open. SPY uses the same dates. Missing boundary prices cause failure. Forward returns are excluded from ranking inputs.

Adjusted open equals open multiplied by adjusted close divided by close. Its exit-to-entry ratio approximates total return; dividend reinvestment at the open has not been independently established. Results are gross with zero costs. This deliberately simple baseline isolates the later contribution of qualitative evidence without requiring unavailable fundamentals.

For filings, the first regular market open after SEC acceptance defines eligibility. The selected NVDA filing was accepted February 26, 2021 and eligible March 1, 2021, before the decision cutoff. The pipeline extracts sections, creates 350-word chunks with 50-word overlap, embeds them with all-MiniLM-L6-v2, and persists them in Chroma. A 24-month lookback and ticker/cutoff filters restrict retrieval before selecting five passages. These are initial engineering settings, not optimized hyperparameters.

[[architecture]]

Figure 1. The price and retrieval paths have executed separately. The manual example uses selected eligible excerpts. Automated generation, structured scoring, and the augmented comparison remain planned.

The query “growth competitive position and business risks” returned five source-matched passages, all from Risk Factors. Index reopening preserved 56 records; wrong-ticker, pre-eligibility, and stale-lookback checks returned no passages. These checks establish operation and filtering [3]. Risk-heavy results motivate separate questions and reviewed relevance judgments.

A separate manual Codex example used three selected excerpts, required evidence IDs, and allowed abstention. The recorded response summarized segment growth and manufacturing dependence, then declined to assign an investment score [4]. Its model revision and sampling settings were unavailable. The session knew later portfolio outcomes, and the agent reviewed its own citations. This example demonstrates an inspectable workflow; it cannot establish predictive quality. No model training or fine-tuning has occurred.

## IV. Preliminary Results

[[returns]]

Figure 2. Recorded gross returns, January 4, 2022 to January 4, 2023, using adjusted-open approximations [1]. Portfolio: equal-weight NVDA and XOM.

The portfolio returned 9.03% versus SPY's -18.74%, an excess of 27.77 percentage points. One of two holdings beat SPY. XOM's gain offset NVDA's loss, so this result leaves the effects of universe choice and market regime unresolved. One cohort cannot establish robust selection skill or a meaningful time-series Sharpe ratio. The result is a baseline for the eventual matched GenAI comparison.

[[example]]

Table 1. One recorded manual example [4]. The original agent self-check marked two observations supported and none unsupported. These counts are not an accuracy estimate; contributor review remains outstanding.

## V. Next Steps

Together, we will establish local inference, review cited outputs, improve data coverage, and validate the matched comparison. We will cross-review model behavior and financial assumptions at each milestone.

[[roadmap]]

Presentation: December 1 or 3.

The final target is a reproducible comparison with matched universe, timing, weights, and costs. If coverage remains inadequate, we will deliver an evaluated filing-analysis prototype alongside the baseline. Fine-tuning and GPU spending require demonstrated need, training data, time, and a justified budget. Session isolation cannot remove future knowledge in pretrained weights.

**Sources:** [1] [Price evidence](https://github.com/DeanDiCarlo/backdating-prediction-ai-project/blob/453faa7a8423557fed65c25698db4876e2db6838/docs/evidence/nick-reproduction.md). [2] [NVIDIA fiscal 2021 10-K, SEC EDGAR](https://www.sec.gov/Archives/edgar/data/1045810/000104581021000010/nvda-20210131.htm). [3] [Retrieval audit](https://github.com/DeanDiCarlo/backdating-prediction-ai-project/blob/453faa7a8423557fed65c25698db4876e2db6838/docs/evidence/live-nvda.md). [4] [Manual example](https://github.com/DeanDiCarlo/backdating-prediction-ai-project/blob/453faa7a8423557fed65c25698db4876e2db6838/docs/evidence/manual-nvda-case.md). Sources [1], [3], and [4] are included in the accompanying FinSight evidence PDF and embedded as text attachments in this PDF. 
