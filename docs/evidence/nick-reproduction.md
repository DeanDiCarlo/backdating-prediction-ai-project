# Original-snapshot reproduction in Nick's workspace

Codex executed this reproduction in Nicholas Stanis's Windows workspace on
2026-11-16 America/New_York (2026-11-17 UTC). This is an agent-run reproduction
in the second contributor's workspace, not a claim that Nick or Dean personally
reviewed the results. Source baseline: `b4c859d`.

Nick supplied the original `yahoo_pilot.csv` and `yahoo_pilot.json` through his
Downloads folder. Both were copied to ignored `data/raw/`; neither is committed.
The CSV SHA-256 is
`d362425e39945c022603aea6a3bf1bf8983cd66512e6f55fa579346128a9bcb2`, matching
both the accompanying metadata and the original evidence note. No prices were
downloaded again.

## Observed checks and results

- 3,108 rows; 518 each for AAPL, MSFT, NVDA, JPM, XOM and SPY.
- Every instrument spans 2020-12-21 through 2023-01-11.
- Zero duplicate ticker/date rows and zero missing adjusted opens/closes.
- Maximum absolute difference between stored adjusted open and
  `open * adj_close / close`: 1.77e-9 (CSV rounding).
- Entry 2022-01-04; exit 2023-01-04; holdings NVDA and XOM.
- Portfolio gross return 9.029157%; SPY -18.743715%; excess 27.772872
  percentage points; stock hit rate 50% (one of two holdings).
- NVDA momentum 125.482130%, forward return -51.842578%; XOM momentum
  57.575534%, forward return 69.900892%.

Environment: Python 3.14.2, pandas 3.1.1, exchange-calendars 4.13.3,
yfinance 0.2.66, pytest 9.2.0. The original recorded snapshot was downloaded
with yfinance 0.2.66; the offline reproduction does not contact Yahoo.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev,quant]'
Get-FileHash data/raw/yahoo_pilot.csv -Algorithm SHA256
.\.venv\Scripts\python.exe -m scripts.quant.run_pilot --snapshot data/raw/yahoo_pilot.csv --output outputs/nick-reproduction
.\.venv\Scripts\python.exe -m pytest -q -ra
```

Initial full-suite execution returned 14 passed, three skipped, four pandas
deprecation warnings. Two skips were missing optional Chroma; one was the
opt-in live SEC test. Later verification, if performed, is recorded separately.
A focused regression test now checks that deleting or changing future prices
cannot alter the historical ranking; its result is recorded in the PR.

This establishes offline reproducibility of the saved snapshot, not independent
verification of Yahoo's dividend adjustments. Adjusted-open ratios remain an
approximation. The fixed universe, one cohort, two holdings and zero costs
remain limitations. Human protocol sign-off and final claim review are pending.
