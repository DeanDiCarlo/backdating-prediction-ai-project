"""Download a reproducible Yahoo snapshot or evaluate an existing one."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from src.quant.pilot import evaluate, price, rank

TICKERS = ['AAPL', 'MSFT', 'NVDA', 'JPM', 'XOM']
ALL = TICKERS + ['SPY']
PARAMS = dict(start='2020-12-20', end='2023-01-12', interval='1d', auto_adjust=False,
              actions=True, threads=False, progress=False, repair=False, keepna=True)
CUTOFF = datetime(2022, 1, 3, 9, 30, tzinfo=ZoneInfo('America/New_York'))


def download(path):
    import yfinance as yf
    raw = yf.download(ALL, **PARAMS)
    frames = []
    for ticker in ALL:
        frame = raw.xs(ticker, axis=1, level='Ticker').copy()
        frame.index = pd.to_datetime(frame.index).strftime('%Y-%m-%d')
        frame.index.name = 'date'
        frame = frame.reset_index().rename(columns={'Open': 'open', 'Close': 'close', 'Adj Close': 'adj_close', 'Dividends': 'dividends', 'Stock Splits': 'splits'})
        frame['ticker'] = ticker
        frame['adj_open'] = frame['open'] * frame['adj_close'] / frame['close']
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    # Fail before writing a snapshot when any required boundary is unusable.
    features = rank(data, TICKERS, CUTOFF)
    for ticker in ALL:
        for day, field in [('2020-12-31', 'adj_close'), ('2021-12-31', 'adj_close'), ('2022-01-04', 'adj_open'), ('2023-01-04', 'adj_open')]:
            from datetime import date
            price(data, ticker, date.fromisoformat(day), field)
    evaluate(data, features, CUTOFF)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False, float_format='%.12g')
    meta = {'retrieved_at_utc': datetime.now(timezone.utc).isoformat(), 'yfinance_version': yf.__version__, 'parameters': PARAMS, 'tickers': ALL,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'coverage': {t: {'rows': int(len(g)), 'first': str(g.date.min()), 'last': str(g.date.max()), 'missing_adj_close': int(g.adj_close.isna().sum()), 'missing_adj_open': int(g.adj_open.isna().sum())} for t, g in data.groupby('ticker')}}
    path.with_suffix('.json').write_text(json.dumps(meta, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--snapshot', default='data/raw/yahoo_pilot.csv')
    parser.add_argument('--output', default='outputs/yahoo_pilot')
    args = parser.parse_args()
    path = Path(args.snapshot)
    if args.download:
        download(path)
    data = pd.read_csv(path, dtype={'date': str})
    features = rank(data, TICKERS, CUTOFF)
    result = evaluate(data, features, CUTOFF)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    pd.DataFrame(result['holdings']).to_csv(out / 'holdings.csv', index=False)
    pd.DataFrame([{'ticker': f.ticker, 'score': f.quant_score, 'available_at': f.feature_available_at.isoformat(), **f.metadata} for f in features]).to_csv(out / 'ranking.csv', index=False)
    labels = [(h['ticker'], h['forward_return']) for h in result['holdings']] + [('Portfolio', result['portfolio_return']), ('SPY', result['benchmark_return'])]
    bars = ''.join(f'<text x="10" y="{40+i*45}">{name}</text><rect x="200" y="{25+i*45}" width="{abs(value)*300:.2f}" height="20" fill="{"#c45b4c" if value < 0 else "#438b79"}"/><text x="{210+abs(value)*300:.2f}" y="{40+i*45}">{value:.2%}</text>' for i, (name, value) in enumerate(labels))
    (out / 'returns.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="220" font-family="sans-serif" font-size="14"><title>Single-cohort returns</title>{bars}</svg>')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
