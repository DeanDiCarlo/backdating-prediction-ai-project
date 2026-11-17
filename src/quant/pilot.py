"""Point-in-time momentum ranking and single-cohort evaluation."""
from datetime import date, datetime, timedelta
from math import isfinite
from zoneinfo import ZoneInfo

from src.common.dates import exchange_session_open, next_execution_open, shift_months
from src.common.schemas import QuantFeature


def session_on_or_before(day):
    for i in range(15):
        candidate = day - timedelta(days=i)
        if exchange_session_open(candidate) is not None:
            return candidate
    raise ValueError('No prior XNYS session')


def session_on_or_after(day):
    for i in range(15):
        candidate = day + timedelta(days=i)
        if exchange_session_open(candidate) is not None:
            return candidate
    raise ValueError('No subsequent XNYS session')


def price(data, ticker, day, field):
    rows = data[(data.ticker == ticker) & (data.date == day.isoformat())]
    if len(rows) != 1:
        raise ValueError(f'Missing or duplicate {ticker} {day} {field}')
    value = float(rows.iloc[0][field])
    if not isfinite(value) or value <= 0:
        raise ValueError(f'Invalid {ticker} {day} {field}')
    return value


def rank(data, tickers, cutoff):
    if cutoff.tzinfo is None:
        raise ValueError('Cutoff must be timezone aware')
    local = cutoff.astimezone(ZoneInfo('America/New_York'))
    # Daily closes are eligible only after the session has closed.
    import exchange_calendars as xc
    cal = xc.get_calendar('XNYS')
    day = session_on_or_before(local.date())
    if cal.session_close(day.isoformat()).to_pydatetime() > cutoff:
        day = session_on_or_before(day - timedelta(days=1))
    previous = session_on_or_before(shift_months(day, -12))
    ranked = sorted(((t, price(data, t, day, 'adj_close') / price(data, t, previous, 'adj_close') - 1) for t in tickers), key=lambda x: (-x[1], x[0]))
    available = cal.session_close(day.isoformat()).to_pydatetime()
    return [QuantFeature(t, local.date(), (len(ranked)-i-1)/(len(ranked)-1) if len(ranked)>1 else 1.0, available,
                         {'momentum': m, 'rank': i+1, 'start_date': previous.isoformat(), 'end_date': day.isoformat(), 'source': 'Yahoo Finance via yfinance', 'price': 'adjusted close'})
            for i, (t, m) in enumerate(ranked)]


def evaluate(data, features, cutoff, benchmark='SPY', count=2):
    if len(features) < count or count < 1:
        raise ValueError('Insufficient ranked features')
    if any(f.feature_available_at > cutoff for f in features):
        raise ValueError('Feature unavailable at cutoff')
    entry = next_execution_open(cutoff).astimezone(ZoneInfo('America/New_York')).date()
    exit = session_on_or_after(shift_months(entry, 12))
    def ret(t):
        return price(data, t, exit, 'adj_open') / price(data, t, entry, 'adj_open') - 1
    spy = ret(benchmark)
    holdings = [{'ticker': f.ticker, 'rank': f.metadata['rank'], 'score': f.quant_score,
                 'momentum': f.metadata['momentum'], 'forward_return': ret(f.ticker)} for f in features[:count]]
    portfolio = sum(h['forward_return'] for h in holdings) / count
    return {'entry': entry.isoformat(), 'exit': exit.isoformat(), 'holdings': holdings,
            'portfolio_return': portfolio, 'benchmark_return': spy, 'excess_return': portfolio-spy,
            'hit_rate': sum(h['forward_return'] > spy for h in holdings)/count}
