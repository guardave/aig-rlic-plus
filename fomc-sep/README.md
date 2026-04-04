# FOMC SEP Extractor

Extracts all 70 FOMC Summary of Economic Projections (SEP) documents from 2007 to present and converts them into structured datasets.

## Document Format Eras

The Fed changed the SEP document format three times. Extraction handles all three:

| Era | Period | Meetings | Content | Extraction Method |
|-----|--------|:--------:|---------|-------------------|
| **A: Compilation** | 2007-10 to 2011-01 | 11 | Full compilation with individual narratives. No median, no dot plot. | PDF extraction (pdfplumber) |
| **B: Summary** | 2011-06 to 2020-09 | 37 | Summary tables + dot plot only. Median introduced Jan 2012. | HTML scraping (primary) + PDF fallback |
| **C: Extended** | 2020-12 to present | 22 | Summary tables + dot plot + individual narratives (returned post-COVID). | HTML scraping (primary) + PDF fallback |

See [`docs/data_dictionary.md`](docs/data_dictionary.md) for full format details per era.

## What's Extracted

| Data | Source | Coverage | Format |
|------|--------|----------|--------|
| Summary stats (median, CT, range) | FRED API (48 series) | 2009-2026 | Parquet |
| Full projection tables (Table 1) | Fed HTML pages | 2012-2026 (expanding to 2007) | Parquet |
| Individual dot plot positions | Fed HTML pages | 2012-2026 (1,448 entries) | Parquet + CSV |
| Source PDFs | Fed website | **All 70 meetings** (2007-2026) | PDF |
| Meeting registry | Compiled | All 70 meetings | JSON |

## Variables Covered

- Real GDP growth
- Unemployment rate
- PCE inflation
- Core PCE inflation
- Federal funds rate (2012+ only)

For each: current year, +1 year, +2 years, longer run projections.

## Project Structure

```
fomc-sep/
├── scripts/
│   ├── 01_fred_sep_series.py      # Phase 1: FRED API extraction
│   ├── 02_meeting_dates.py        # Phase 2: Meeting date discovery + era classification
│   ├── 03_scrape_html_tables.py   # Phase 3: HTML table extraction (Era B+C)
│   ├── 04_parse_pdf_era_a.py      # Phase 4: PDF extraction for Era A (2007-2011)
│   ├── 05_parse_pdf_era_bc.py     # Phase 5: PDF fallback for Era B+C (6 meetings without HTML)
│   └── 06_validate.py             # Phase 6: Cross-validation (FRED vs scraped)
├── data/
│   ├── references/                # 70 source PDFs (one per meeting, all eras)
│   ├── sep_tables_raw/            # 54 scraped HTML pages (Era B+C)
│   ├── fred/                      # FRED API outputs (5 variable files + combined)
│   ├── sep_meeting_registry.json  # Meeting registry with era tags
│   ├── sep_projections.parquet    # Consolidated projection dataset (all eras)
│   ├── sep_dot_plot.parquet       # Dot plot data (Era B+C, 1,448 entries)
│   └── sep_dot_plot.csv           # CSV version for easy inspection
├── app/
│   └── sep_viewer.py              # Streamlit dashboard
├── docs/
│   └── data_dictionary.md         # Schema, eras, extraction strategy, known gaps
└── README.md
```

## Usage

```bash
# Phase 1: Pull FRED summary stats
python fomc-sep/scripts/01_fred_sep_series.py

# Phase 2: Discover meeting dates + classify eras
python fomc-sep/scripts/02_meeting_dates.py

# Phase 3: Scrape HTML tables (Era B+C)
python fomc-sep/scripts/03_scrape_html_tables.py

# Phase 4-5: Parse PDFs (Era A + fallback)
python fomc-sep/scripts/04_parse_pdf_era_a.py
python fomc-sep/scripts/05_parse_pdf_era_bc.py

# Phase 6: Validate
python fomc-sep/scripts/06_validate.py

# Launch viewer
cd fomc-sep/app && streamlit run sep_viewer.py
```

## Data Sources

- [FRED SEP Release (48+ series)](https://fred.stlouisfed.org/release?rid=326)
- [Fed HTML accessible pages](https://www.federalreserve.gov/monetarypolicy/fomcprojtabl{YYYYMMDD}.htm) (Era B+C)
- [Fed PDF — standard format](https://www.federalreserve.gov/monetarypolicy/files/fomcprojtabl{YYYYMMDD}.pdf) (Era B+C)
- [Fed PDF — compilation format](https://www.federalreserve.gov/monetarypolicy/files/FOMC{YYYYMMDD}SEPcompilation.pdf) (Era A)

## Status

| Phase | Status | Output |
|-------|:------:|--------|
| 1. FRED extraction | Done | 48 series, 914 obs |
| 2. Meeting discovery | Done | 70 meetings, era-tagged |
| 3. HTML scraping (Era B+C) | Done | 1,448 dot entries, 160 Table 1 rows |
| 4. PDF parsing (Era A) | Pending | 11 meetings need pdfplumber extraction |
| 5. PDF fallback (Era B+C) | Pending | 6 meetings without HTML |
| 6. Validation | Pending | Cross-check FRED vs scraped |
| Streamlit viewer | Done | Dot plot explorer, FRED projections, registry |
| Reference PDFs | Done | **70/70** downloaded |
