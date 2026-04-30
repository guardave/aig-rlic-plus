# AIG-RLIC+ Research Portal

This project builds a Streamlit portal and reproducible research pipeline for the HY-IG credit spread vs SPY analysis.

## Setup

Install the full project dependency set from the repository root:

```bash
pip install -r requirements.txt
```

Set `FRED_API_KEY` in the environment before refreshing source data. The scripts do not include a default API key.

## Pipeline Order

Run the research pipeline in this order when regenerating artifacts:

```bash
python scripts/data_pipeline_hy_ig_spy.py
python scripts/stage1_exploratory.py
python scripts/stage2_core_models.py
python scripts/tournament_backtest.py
python scripts/tournament_validation.py
python scripts/generate_charts.py
```

The chart generation step expects upstream parquet and CSV artifacts from the earlier stages. If an artifact is missing, rerun the corresponding upstream stage instead of relying on stale checked-in charts.

## Optional Legacy ICE/BofA Archive

FRED now exposes only about three years of observations for the ICE/BofA OAS series. If you have reviewed the FRED/ICE terms and want to build a local research archive from public Wayback captures, run:

```bash
python scripts/fetch_fred_wayback_archive.py --accept-ice-terms
```

This writes `data/legacy_fred_archive/ice_bofa_oas_wayback.csv`. The data pipeline automatically merges that local archive with current FRED observations when the file exists.

## App

Start the portal with:

```bash
streamlit run app/app.py
```
