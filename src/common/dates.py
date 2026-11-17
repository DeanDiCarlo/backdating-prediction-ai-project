"""Decision, execution, and forward-label date conventions."""
from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Callable
from zoneinfo import ZoneInfo


@lru_cache(maxsize=4096)
def exchange_session_open(day: date) -> datetime | None:
    """Return the regular XNYS open in UTC, or None for a closed date."""
    try:
        import exchange_calendars as calendars
    except ImportError as exc:
        raise RuntimeError("Install exchange-calendars for market-session eligibility") from exc
    calendar = calendars.get_calendar("XNYS")
    if not calendar.is_session(day.isoformat()):
        return None
    return calendar.session_open(day.isoformat()).to_pydatetime()


def next_execution_open(cutoff: datetime,
                        session_open: Callable[[date], datetime | None] = exchange_session_open) -> datetime:
    if cutoff.tzinfo is None:
        raise ValueError("Decision cutoff must be timezone aware")
    local_day = cutoff.astimezone(ZoneInfo("America/New_York")).date()
    for offset in range(15):
        opening = session_open(local_day + timedelta(days=offset))
        if opening is not None and opening > cutoff:
            return opening
    raise ValueError("No execution session found within 15 days")


def shift_months(start: date, months: int) -> date:
    month_index = start.year * 12 + start.month - 1 + months
    year, month_zero = divmod(month_index, 12)
    month = month_zero + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def horizon_date(start: date, months: int) -> date:
    if months < 1:
        raise ValueError("Horizon months must be positive")
    return shift_months(start, months)


def outcome_complete(entry_date: date, months: int, last_price_date: date,
                     session_open: Callable[[date], datetime | None] = exchange_session_open) -> bool:
    """Require observed prices through the first session on/after the entry-date horizon."""
    target = horizon_date(entry_date, months)
    for offset in range(15):
        day = target + timedelta(days=offset)
        if session_open(day) is not None:
            return last_price_date >= day
    raise ValueError("No horizon session found within 15 days")
