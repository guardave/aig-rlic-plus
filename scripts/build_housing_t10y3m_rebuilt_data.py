"""Build data/{housing_starts,t10y3m}_rebuilt_spy_monthly_latest.parquet from
FRED + yfinance for the #255-floored rebuild pairs (NOT Dana's parquets).
nhs_saar_rebuilt fetches FRED HSN1F inside its own pipeline, so it needs no
separate build. Parquets follow the data/ gitignore convention."""
import os, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from fredapi import Fred
import yfinance as yf
fred = Fred(api_key=os.environ["FRED_API_KEY"])
# resample("ME") labels the in-progress calendar month with its (future) month-end date, so a run on
# 2026-10-09 produced a partial "2026-10-31" row (t10y3m_rebuilt_spy oos_period_end in the future).
# Keep only COMPLETE months. A "label <= today" test still admits a partial month when run on the
# last calendar day, so daily sources (SPY, T10Y3M) use the data-based rule in
# scripts/month_completeness.py: keep a month only if the source's last observation is at/after
# that month's last business day. HOUST is a monthly series: an observation means the month is
# released and complete, so only the future-label guard applies.
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from month_completeness import complete_months
_TODAY = pd.Timestamp.today().normalize()
_spy_d = yf.download("SPY", start="1992-01-01", progress=False, auto_adjust=True, actions=False)["Close"]
if isinstance(_spy_d, pd.DataFrame): _spy_d = _spy_d.iloc[:, 0]
_spy_d = _spy_d.dropna()
spy = complete_months(_spy_d.resample("ME").last(), _spy_d.index.max())
spy.name = "spy"
def add_spy(df):
    df = df.join(spy, how="left"); df["spy_ret"] = df["spy"].pct_change()
    for h in (1, 3, 6, 12): df[f"spy_fwd_{h}m"] = df["spy"].pct_change(h).shift(-h)
    return df.loc["1993-01-01":]
# housing starts (HOUST, SAAR level -> pct growth transforms)
h = fred.get_series("HOUST").rename("hst"); h.index = pd.to_datetime(h.index)
_hm = h.resample("ME").last(); hm = _hm[_hm.index <= _TODAY].to_frame()
hm["hst_pct_yoy"] = hm["hst"].pct_change(12) * 100
hm["hst_pct_mom"] = hm["hst"].pct_change(1) * 100
hm["hst_3m_pct_yoy"] = hm["hst_pct_yoy"].rolling(3).mean()
hm["hst_3m_pct"] = hm["hst"].pct_change(3) * 100
hm["hst_yoy_accel_pct"] = hm["hst_pct_yoy"].diff()
hm["hst_yoy_zscore_120m"] = (hm["hst_pct_yoy"] - hm["hst_pct_yoy"].rolling(120, min_periods=60).mean()) / hm["hst_pct_yoy"].rolling(120, min_periods=60).std()
hm["hst_yoy_contraction_flag"] = (hm["hst_pct_yoy"] < 0).astype(float)
hm = add_spy(hm); hm.index.name = "date"
hm.to_parquet("data/housing_starts_rebuilt_spy_monthly_latest.parquet")
# t10y3m (spread in pp -> diff transforms, not pct)
t = fred.get_series("T10Y3M").rename("t10y3m"); t.index = pd.to_datetime(t.index)
t = t.dropna()
tm = complete_months(t.resample("ME").last(), t.index.max()).to_frame()
tm["t10y3m_mom"] = tm["t10y3m"].diff(1)
tm["t10y3m_3m_chg"] = tm["t10y3m"].diff(3)
tm["t10y3m_6m_chg"] = tm["t10y3m"].diff(6)
tm["t10y3m_12m_chg"] = tm["t10y3m"].diff(12)
tm["t10y3m_zscore_60m"] = (tm["t10y3m"] - tm["t10y3m"].rolling(60, min_periods=36).mean()) / tm["t10y3m"].rolling(60, min_periods=36).std()
tm["t10y3m_inversion_flag"] = (tm["t10y3m"] < 0).astype(float)
tm["t10y3m_curve_steepening"] = (tm["t10y3m"].diff(1) > 0).astype(float)
tm = add_spy(tm); tm.index.name = "date"
tm.to_parquet("data/t10y3m_rebuilt_spy_monthly_latest.parquet")
print("built housing_starts + t10y3m rebuilt parquets")
