# Experiment contract (implemented pilot; contributor sign-off tracked in #5)

- **Unit:** (`ticker`, `as_of_date`); dates in ISO 8601.
- **Universe:** fixed pilot stock list; production universe must be based on membership known on each historical date.
- **Date convention:** as_of_date is a market decision date. The pilot cutoff is 09:30 America/New_York; execution is the next regular XNYS open strictly after the cutoff. SEC filings become eligible at the first regular XNYS open strictly after acceptance; unknown acceptance times are ineligible. This is a conservative proxy, not proof of first public availability.
- **Horizon:** the implemented pilot uses 12 months; see the frozen protocol below.
- **Completed label:** require daily prices through the first trading session on or after the 12-month horizon. Incomplete outcomes are never training or evaluation labels.
- **Quant output:** `ticker,as_of_date,quant_score`.
- **GenAI output:** `ticker,as_of_date,qualitative_score,filing_accession,filing_available_at,evidence`.
- **Joined evaluation:** forward returns and SPY returns are generated *after* scores and never passed to predictors.
- **Score normalization:** define and freeze on training/history only; do not normalize using out-of-sample evaluation rows if this would leak.
- **Missing evidence:** report missing coverage rather than hallucinating an analysis.
- **Baselines:** evaluate SPY, quant-only, and quant+GenAI on the same dates, tickers, rebalance rules, portfolio weighting and costs.
- **Metrics:** excess return, Sharpe (with stated risk-free convention), volatility, drawdown, and hit rate of stocks exceeding SPY. Include a clear return calculation.
- **Midterm proof:** one reproducible quant backtest slice and one filing-grounded model output, with limitations clearly distinguished from final results.

## Frozen Yahoo midterm pilot

The preliminary pilot uses Yahoo Finance via pinned yfinance 0.2.66 for AAPL, MSFT, NVDA, JPM, XOM and SPY. FactSet entitlement is a separate future investigation, not a dependency. At 2022-01-03 09:30 New York, rank the five stocks by adjusted-close return from the last XNYS session on or before the prior-year anniversary through the last completed session. Break ties alphabetically; scores are `(N - rank)/(N - 1)` and availability is that session's close. Fail on missing or invalid boundary prices rather than substituting a different session. Choose the top two at equal weight.

Entry is the next regular open, 2022-01-04; exit is the first regular open on or after the 12-month anniversary, 2023-01-04. Use open multiplied by adjusted close / close for each boundary; its ratio approximates total return and does not prove dividend reinvestment at the open. Compare SPY on identical dates, report gross zero-cost return, excess and stock hit rate. One annual observation is not a quarterly backtest and cannot support Sharpe. See [pilot evidence](evidence/yahoo-pilot.md) for provenance, reproduction and limitations. Point-in-time fundamentals and the matched GenAI investment comparison remain future work; the real filing-grounded case study is separate.
