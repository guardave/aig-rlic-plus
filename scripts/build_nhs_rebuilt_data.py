"""Build data/nhs_rebuilt_spy_monthly_latest.parquet from FRED + yfinance.
Clean, documented rebuild (NOT a byte-replica of Dana's parquet) for the
#255-floored nhs_rebuilt_spy pair. NSA=HSN1FNSA, SA=HSN1F (FRED SAAR)."""
import os, numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from fredapi import Fred
import yfinance as yf

fred=Fred(api_key=os.environ["FRED_API_KEY"])
nsa=fred.get_series("HSN1FNSA").rename("nhs_nsa")   # New 1-family houses sold, NSA (000s)
sa =fred.get_series("HSN1F").rename("nhs_sa")        # same, SAAR
idx=pd.date_range(nsa.index.min(), nsa.index.max(), freq="MS")
df=pd.DataFrame(index=idx)
df["nhs_nsa"]=nsa.reindex(idx); df["nhs_sa"]=sa.reindex(idx)
# move to month-END index (project convention)
df.index=df.index+pd.offsets.MonthEnd(0)
# --- NHS signals ---
df["nhs_pct_yoy"]=df["nhs_nsa"].pct_change(12)*100.0
df["nhs_yoy_accel_pct"]=df["nhs_pct_yoy"].diff()
df["nhs_3m_pct_yoy"]=df["nhs_pct_yoy"].rolling(3).mean()
df["nhs_sa_pct_mom"]=df["nhs_sa"].pct_change(1)*100.0
df["nhs_sa_3m_pct"]=df["nhs_sa"].pct_change(3)*100.0
df["nhs_yoy_zscore_120m"]=(df["nhs_pct_yoy"]-df["nhs_pct_yoy"].rolling(120,min_periods=60).mean())/df["nhs_pct_yoy"].rolling(120,min_periods=60).std()
df["nhs_yoy_contraction_flag"]=(df["nhs_pct_yoy"]<0).astype(float)
# --- SPY (month-end, total return via auto_adjust) ---
spy=yf.download("SPY", start="1992-01-01", progress=False, auto_adjust=True, actions=False)["Close"]
spy=spy.resample("ME").last()
if isinstance(spy, pd.DataFrame): spy=spy.iloc[:,0]
spy.name="spy"
df=df.join(spy, how="left")
df["spy_ret"]=df["spy"].pct_change()
for h in (1,3,6,12):
    df[f"spy_fwd_{h}m"]=df["spy"].pct_change(h).shift(-h)
# SPY-bound from 1993
df=df.loc["1993-01-01":]
df.index.name="date"
cols=['nhs_nsa','nhs_pct_yoy','nhs_yoy_accel_pct','nhs_3m_pct_yoy','nhs_sa','nhs_sa_pct_mom','nhs_sa_3m_pct','nhs_yoy_zscore_120m','nhs_yoy_contraction_flag','spy','spy_ret','spy_fwd_1m','spy_fwd_3m','spy_fwd_6m','spy_fwd_12m']
out=df[cols]
out.to_parquet("data/nhs_rebuilt_spy_monthly_latest.parquet")
print("built:", out.shape, "|", str(out.index.min().date()), "->", str(out.index.max().date()))
print("nhs_pct_yoy 2009 min:", round(out.loc['2009','nhs_pct_yoy'].min(),1), "(expect <-20)")
print("nhs_pct_yoy 2023 min:", round(out.loc['2023','nhs_pct_yoy'].min(),1), "(expect <0)")
print("contraction_flag sum:", int(out['nhs_yoy_contraction_flag'].sum()))
print("spy_ret abs max:", round(out['spy_ret'].abs().max(),3), "(expect <0.4)")
