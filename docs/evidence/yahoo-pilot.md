# Yahoo Finance momentum pilot

One cohort, five fixed stocks, decision 2022-01-03 09:30 America/New_York. Ranking uses adjusted closes on 2020-12-31 and 2021-12-31; the top two enter at the 2022-01-04 XNYS open and exit at the 2023-01-04 open. This is preliminary price momentum, not a quarterly backtest or a GenAI comparison.

| Holding | Trailing momentum | Forward return | Weight |
| --- | ---: | ---: | ---: |
| NVDA | 125.48% | -51.84% | 50% |
| XOM | 57.58% | 69.90% | 50% |
| Portfolio | | 9.03% | 100% |
| SPY | | -18.74% | |

Portfolio excess over SPY: 27.77 percentage points; stock hit rate versus SPY: 1/2 (50%). Gross, zero trading costs. There is one decision and two holdings; Sharpe and other time-series risk metrics are not meaningful here. The fixed universe introduces survivorship and selection bias; results are highly sensitive to the cohort and period. Fundamentals, a real filing-grounded case study, and matched quant-plus-GenAI comparison remain future work. No incremental GenAI value is inferred.

## Data quality and independent check

Snapshot retrieved 2026-11-17 01:21:48 UTC with yfinance 0.2.66; CSV SHA-256 `d362425e39945c022603aea6a3bf1bf8983cd66512e6f55fa579346128a9bcb2`. Each of AAPL, MSFT, NVDA, JPM, XOM and SPY has 518 rows, 2020-12-21 through 2023-01-11, with zero missing adjusted closes or adjusted opens. All six have valid prices on the four relevant boundary dates. Exact request parameters, counts and hash are saved beside the ignored snapshot. The end parameter is exclusive.

Yahoo's adjusted open is calculated as `open * adjusted_close / close`. Its ratio approximates total return; it does not establish reinvestment of dividends at the open. Yahoo's historical adjustments may change as later corporate actions occur. NVDA shows a 4-for-1 split on 2021-07-20, matching [NVIDIA's split FAQ](https://investor.nvidia.com/files/doc_downloads/doc_faq/08/Investor-NVIDIA-2021-Stock-Split-FAQ-08.9.2021.pdf). Yahoo's split-adjusted 2020-12-31 NVDA close of 13.055 agrees with the independently published [SEC historical price table](https://www.sec.gov/Archives/edgar/data/1419828/000119312525330743/nvdac196_prelim.htm), which states adjustment for the 2021 and 2024 splits. The dividend-adjusted close (12.988001) and derived adjusted opens have not been independently matched to another total-return series; this remains an unresolved verification limitation.

## Reproduce

Python 3.11+ and network access are needed for the first command. Share the ignored snapshot and its JSON metadata separately under applicable data terms; a new download may differ from the recorded snapshot. From the repository root:

```sh
python -m venv .venv
.venv/bin/python -m pip install -e '.[quant,dev]'
.venv/bin/python -m scripts.quant.run_pilot --download
.venv/bin/python -m scripts.quant.run_pilot --snapshot data/raw/yahoo_pilot.csv
.venv/bin/python -m pytest -q
```

The second run uses the saved snapshot without network access. It writes ranking, holdings, JSON results and `returns.svg` under `outputs/yahoo_pilot/`. The snapshot and outputs are ignored, not committed. Compare its SHA-256 with the metadata before reproducing this particular table.
