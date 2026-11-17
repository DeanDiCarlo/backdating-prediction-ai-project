# Experiment contract (v0; agree before coding)

- **Unit:** (`ticker`, `as_of_date`); dates in ISO 8601.
- **Universe:** fixed pilot stock list; production universe must be based on membership known on each historical date.
- **Date convention:** as_of_date is a market decision date. The pilot cutoff is 09:30 America/New_York; execution is the next regular XNYS open strictly after the cutoff. SEC filings become eligible at the first regular XNYS open strictly after acceptance; unknown acceptance times are ineligible. This is a conservative proxy, not proof of first public availability.
- **Horizon:** choose a single forward holding period (suggest 12 months for the long-term hypothesis).
- **Completed label:** require daily prices through the first trading session on or after the 12-month horizon. Incomplete outcomes are never training or evaluation labels.
- **Quant output:** `ticker,as_of_date,quant_score`.
- **GenAI output:** `ticker,as_of_date,qualitative_score,filing_accession,filing_available_at,evidence`.
- **Joined evaluation:** forward returns and SPY returns are generated *after* scores and never passed to predictors.
- **Score normalization:** define and freeze on training/history only; do not normalize using out-of-sample evaluation rows if this would leak.
- **Missing evidence:** report missing coverage rather than hallucinating an analysis.
- **Baselines:** evaluate SPY, quant-only, and quant+GenAI on the same dates, tickers, rebalance rules, portfolio weighting and costs.
- **Metrics:** excess return, Sharpe (with stated risk-free convention), volatility, drawdown, and hit rate of stocks exceeding SPY. Include a clear return calculation.
- **Midterm proof:** one reproducible quant backtest slice and one filing-grounded model output, with limitations clearly distinguished from final results.
