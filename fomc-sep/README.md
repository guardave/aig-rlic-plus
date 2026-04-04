# FOMC SEP Extractor

Extracts all available FOMC Summary of Economic Projections (SEP) documents from 2007 to present and converts them into structured datasets.

## What's Extracted

| Data | Source | Format |
|------|--------|--------|
| Summary stats (median, central tendency, range) | FRED API (63 series) | Parquet |
| Full projection tables (Table 1) | Fed HTML accessible pages | Parquet |
| Individual dot plot positions (Table 2, 2012+) | Fed HTML accessible pages | Parquet |
| Meeting metadata (dates, participants) | Fed website | CSV |

## Variables Covered

- Real GDP growth
- Unemployment rate
- PCE inflation
- Core PCE inflation
- Federal funds rate

For each: current year, +1 year, +2 years, longer run projections.

## Project Structure

```
fomc-sep/
├── scripts/
│   ├── 01_fred_sep_series.py      # FRED API extraction
│   ├── 02_meeting_dates.py        # Discover all SEP meeting dates
│   ├── 03_scrape_html_tables.py   # HTML table extraction
│   ├── 04_parse_pdf_fallback.py   # PDF fallback for unavailable HTML
│   ├── 05_reconstruct_dots.py     # Dot plot reconstruction
│   └── 06_validate.py             # Cross-validation
├── data/
│   ├── fred/                      # FRED API outputs
│   ├── sep_tables_raw/            # Raw scraped tables per meeting
│   ├── sep_projections.parquet    # Consolidated projection dataset
│   └── dot_plot.parquet           # Individual dot positions
├── app/
│   └── sep_viewer.py              # Streamlit dashboard
├── docs/
│   └── data_dictionary.md
└── README.md
```

## Usage

```bash
# Phase 1: Pull FRED summary stats
python fomc-sep/scripts/01_fred_sep_series.py

# Phase 2: Discover meeting dates
python fomc-sep/scripts/02_meeting_dates.py

# Phase 3: Scrape HTML tables
python fomc-sep/scripts/03_scrape_html_tables.py

# Phase 4: Validate
python fomc-sep/scripts/06_validate.py

# Launch viewer
cd fomc-sep/app && streamlit run sep_viewer.py
```

## Data Sources

- [FRED SEP Release (63 series)](https://fred.stlouisfed.org/release?rid=326)
- [Fed HTML accessible pages](https://www.federalreserve.gov/monetarypolicy/fomcprojtabl{YYYYMMDD}.htm)
- [Fed PDF projection tables](https://www.federalreserve.gov/monetarypolicy/files/fomcprojtabl{YYYYMMDD}.pdf)
