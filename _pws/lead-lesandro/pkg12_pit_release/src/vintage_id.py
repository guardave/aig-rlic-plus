"""pkg12 D8: which vintage do the data panels hold? For each FRED-backed pair, find the ALFRED vintage whose values
match the panel's raw column (rtol 2e-4), and the match rate against the vintage of 2026-10-16 and against first prints.
Usage: python _pws/lead-lesandro/pkg12_pit_release/src/vintage_id.py OUT.csv [DATA_DIR]"""
import pandas as pd, numpy as np, glob, os, sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[4]
V=str(REPO/'data'/'release_calendar'/'vintages')
D=sys.argv[2] if len(sys.argv)>2 else '/workspaces/aig-rlic-plus/data'
MAP={"busloans_spy":("BUSLOANS","busloans_spy_monthly_latest.parquet","busloans_usd",None),
"cass_freight_spy":("FRGSHPUSM649NCIS","cass_freight_spy_monthly_latest.parquet","cass_freight_idx",None),
"cc_delinquency_spy":("DRCCLACBN","cc_delinquency_spy_quarterly_latest.parquet","ccdelinq",None),
"consumer_sentiment_spy":("UMCSENT","consumer_sentiment_spy_monthly_latest.parquet","umcsent",None),
"umcsent_xlv":("UMCSENT","umcsent_xlv_monthly_19980101_20251231.parquet","umcsent",None),
"housing_starts_rebuilt_spy":("HOUST","housing_starts_rebuilt_spy_monthly_latest.parquet","hst",None),
"import_price_spy":("IR","import_price_spy_monthly_latest.parquet","import_price",None),
"indpro_spy":("INDPRO","indpro_spy_monthly_19900101_20251231.parquet","indpro",None),
"indpro_xlp":("INDPRO","indpro_xlp_monthly_19980101_20251231.parquet","indpro",None),
"m2sl_yoy_spy":("M2SL","m2sl_yoy_spy_monthly_latest.parquet","m2sl_usd",None),
"mfg_new_orders_spy":("NEWORDER","mfg_new_orders_spy_monthly_latest.parquet","mfg_new_orders",None),
"nhs_rebuilt_spy":("HSN1FNSA","nhs_rebuilt_spy_monthly_latest.parquet","nhs_nsa",None),
"nhs_saar_rebuilt_spy":("HSN1F","nhs_saar_rebuilt_spy_monthly_latest.parquet","hsn1f",None),
"permit_yoy_spy":("PERMIT","permit_yoy_spy_monthly_latest.parquet","permit_yoy","yoy"),
"permit_spy":("PERMIT","permit_spy_monthly_20261008.parquet","permit",None),
"retail_inv_sales_spy":("RETAILIRSA","retail_inv_sales_spy_monthly_latest.parquet","invsales",None),
"rsxfs_spy":("RSXFS","rsxfs_spy_monthly_latest.parquet","rsxfs",None),
"sloos_ci_small_spy":("DRTSCILM","sloos_ci_small_spy_quarterly_latest.parquet","sloos_ci_small",None),
"unrate_spy":("UNRATE","unrate_spy_monthly_latest.parquet","unrate",None)}
def load(sid):
    d=pd.read_csv(f'{V}/{sid}.csv.gz',parse_dates=['date','realtime_start'])
    d['realtime_end']=pd.to_datetime(d.realtime_end.replace('9999-12-31','2262-01-01'))
    d['value']=d.value.astype(float); return d
def asof(d,v):
    x=d[(d.realtime_start<=v)&(d.realtime_end>=v)]
    return x.set_index('date').value.sort_index()
def per(s,q):  # stamp -> period
    return s.index.to_period('Q' if q else 'M')
if __name__=='__main__':
    out=[]
    for p,(sid,f,col,tr) in MAP.items():
        d=load(sid); q=sid in ('DRCCLACBN','DRTSCILM')
        pan=pd.read_parquet(f'{D}/{f}')[col].dropna()
        pan.index=pan.index.to_period('Q' if q else 'M')
        cands=sorted(d.realtime_start.unique())
        best=(None,-1,0)
        for v in cands[::-1][:400]:
            s=asof(d,pd.Timestamp(v)); s.index=s.index.to_period('Q' if q else 'M')
            if tr=='yoy': s=(s/s.shift(12 if not q else 4)-1)*100
            ov=pan.index.intersection(s.dropna().index)
            if len(ov)<12: continue
            a,b=pan.loc[ov].values,s.loc[ov].values
            m=np.isclose(a,b,rtol=2e-4,atol=1e-6).mean()
            if m>best[1]: best=(pd.Timestamp(v).date(),m,len(ov))
            if m==1.0: break
        # latest
        s=asof(d,pd.Timestamp('2026-10-16')); s.index=s.index.to_period('Q' if q else 'M')
        if tr=='yoy': s=(s/s.shift(12)-1)*100
        ov=pan.index.intersection(s.dropna().index)
        ml=np.isclose(pan.loc[ov].values,s.loc[ov].values,rtol=2e-4,atol=1e-6).mean()
        # first-release
        fr=d.sort_values('realtime_start').groupby('date').first().value; fr.index=fr.index.to_period('Q' if q else 'M')
        ovf=pan.index.intersection(fr.index)
        if tr=='yoy': mf=np.nan
        else: mf=np.isclose(pan.loc[ovf].values,fr.loc[ovf].values,rtol=2e-4,atol=1e-6).mean()
        out.append(dict(pair=p,series=sid,panel=f,panel_last=str(pan.index.max()),best_vintage=best[0],best_match=round(best[1],4),n=best[2],match_latest_20261016=round(ml,4),match_first_release=round(mf,4) if mf==mf else None))
        print(out[-1],flush=True)
    pd.DataFrame(out).to_csv(sys.argv[1] if len(sys.argv)>1 else 'vintage_id.csv',index=False)
