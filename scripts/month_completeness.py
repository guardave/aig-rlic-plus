"""Month-completeness rule for monthly series resampled from a DAILY source.

``resample("ME")`` labels the in-progress calendar month with its (future) month-end date, so a
partial month leaks in. A time check against today is not enough: a run on the last calendar day
of the month, before that day's data is published, still passes ``label <= today``. The rule used
here is data-based: keep a month only if the source's last observation is at or after that month's
last business day (US federal holidays plus Good Friday, which markets observe, are excluded).
"""
from __future__ import annotations

import pandas as pd
from dateutil.easter import easter
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay


def _bday(years) -> CustomBusinessDay:
    gf = [pd.Timestamp(easter(y)) - pd.Timedelta(days=2) for y in years]
    return CustomBusinessDay(calendar=USFederalHolidayCalendar(), holidays=gf)


def last_business_day(label: pd.Timestamp) -> pd.Timestamp:
    """Last business day on or before the month-end ``label``."""
    label = pd.Timestamp(label).normalize()
    return label if _bday([label.year]).is_on_offset(label) else label - _bday([label.year])


def complete_months(monthly: pd.Series | pd.DataFrame, last_obs: pd.Timestamp):
    """Drop month-end rows whose month is not yet complete in the daily source.

    ``last_obs`` is the date of the last observation in the DAILY source series.
    """
    last_obs = pd.Timestamp(last_obs).normalize()
    keep = [last_obs >= last_business_day(m) for m in monthly.index]
    return monthly[keep]
