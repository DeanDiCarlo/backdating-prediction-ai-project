from datetime import date, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from src.common.schemas import QualFeature, join_features
from src.quant.pilot import evaluate, rank, session_on_or_after, session_on_or_before

CUTOFF = datetime(2022, 1, 3, 9, 30, tzinfo=ZoneInfo('America/New_York'))

@pytest.fixture
def data():
    rows = []
    for ticker, end, exit in [('A', 20, 120), ('B', 20, 80), ('C', 15, 90), ('SPY', 10, 110)]:
        for day, close, opening in [('2020-12-31', 10, 100), ('2021-12-31', end, 100), ('2022-01-03', 9999, 100), ('2022-01-04', 10, 100), ('2023-01-04', 10, exit)]:
            rows.append(dict(ticker=ticker, date=day, adj_close=close, adj_open=opening))
    return pd.DataFrame(rows)


def test_ranking_ties_cutoff_and_schema(data):
    features = rank(data, ['B', 'C', 'A'], CUTOFF)
    assert [f.ticker for f in features] == ['A', 'B', 'C']
    assert [f.quant_score for f in features] == [1, .5, 0]
    assert features[0].metadata['end_date'] == '2021-12-31'
    assert features[0].feature_available_at <= CUTOFF
    q = QualFeature('A', date(2022, 1, 3), None, (), (), {})
    assert join_features(features[0], q, CUTOFF)['quant_score'] == 1


def test_sessions_and_evaluation(data):
    assert session_on_or_before(date(2022, 1, 1)) == date(2021, 12, 31)
    assert session_on_or_after(date(2023, 1, 1)) == date(2023, 1, 3)
    result = evaluate(data, rank(data, ['A', 'B', 'C'], CUTOFF), CUTOFF)
    assert (result['entry'], result['exit']) == ('2022-01-04', '2023-01-04')
    assert result['portfolio_return'] == pytest.approx(0)
    assert result['benchmark_return'] == pytest.approx(.1)
    assert result['excess_return'] == pytest.approx(-.1)
    assert result['hit_rate'] == .5


def test_missing_invalid_duplicate_and_incomplete(data):
    with pytest.raises(ValueError):
        rank(data[data.date != '2020-12-31'], ['A'], CUTOFF)
    broken = data.copy()
    broken.loc[(broken.ticker == 'A') & (broken.date == '2021-12-31'), 'adj_close'] = float('nan')
    with pytest.raises(ValueError):
        rank(broken, ['A'], CUTOFF)
    features = rank(data, ['A', 'B'], CUTOFF)
    with pytest.raises(ValueError):
        evaluate(data[data.date != '2023-01-04'], features, CUTOFF)
    with pytest.raises(ValueError):
        rank(pd.concat([data, data.iloc[[0]]]), ['A'], CUTOFF)
