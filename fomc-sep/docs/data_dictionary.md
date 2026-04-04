# FOMC SEP Data Dictionary

## Document Format Eras

The Fed changed the SEP document format three times. Any extraction logic must handle all three eras.

| Era | Period | Meetings | Pages | Size | Source URL Pattern |
|-----|--------|:--------:|:-----:|:----:|-------------------|
| **A: Compilation** | 2007-10 to 2011-01 | 11 | 25-36 | 170-832 KB | `FOMC{DATE}SEPcompilation.pdf` |
| **B: Summary** | 2011-06 to 2020-09 | 36 | 3-6 | 80-310 KB | `fomcprojtabl{DATE}.pdf` |
| **C: Extended** | 2020-12 to present | 23 | 17 | 1,248-1,561 KB | `fomcprojtabl{DATE}.pdf` |

### Era A: Compilation (2007-10 to 2011-01)

- **Title:** "SEP: Compilation and Summary of Individual Economic Projections"
- **Content:** Full compilation including individual participant narratives, projection tables, and uncertainty assessments
- **Structure:** Summary table (central tendency + range only, no median) → individual participant write-ups → charts
- **Key difference:** No median column (medians introduced with dot plots in 2012). No dot plot.
- **Variables:** GDP growth, unemployment rate, PCE inflation (headline + core in some years)
- **No federal funds rate projections** (added with dot plots in January 2012)

### Era B: Summary (2011-06 to 2020-09)

- **Title:** "Embargoed for release at 2:00 p.m..." (pre-2016) or "For release at 2:00 p.m..." (2016+)
- **Content:** Summary tables + dot plot chart only (no individual narratives)
- **Structure:** Table 1 (economic projections: median, central tendency, range) → Figure 1 (dot plot) → Table 2 (historical projection errors)
- **Key change at 2012-01:** Dot plots and median projections introduced
- **Key change at 2014-Q3:** Dot plot increment changed from 0.25% to 0.125%
- **Key change at 2015-Q3:** Added one extra page (6 pages total) in some meetings
- **Variables:** GDP growth, unemployment, PCE inflation, core PCE inflation, federal funds rate
- **Horizons:** Current year, +1 year, +2 year, longer run

### Era C: Extended (2020-12 to present)

- **Title:** "For release at 2:00 p.m..."
- **Content:** Summary tables + dot plot + individual participant narratives (narratives returned post-COVID)
- **Structure:** Table 1 (projections) → Figure 1 (dot plot) → Table 2 (error ranges) → Figure 2 (fan charts) → Individual narratives
- **17 pages consistently**
- **Variables:** Same as Era B
- **Key addition:** Uncertainty/risk assessments, fan charts showing confidence intervals

## Data Extraction Strategy by Era

### Era A: PDF Extraction Required

- No HTML accessible pages available
- Use `pdfplumber` to extract Table 1 from PDF
- Parse central tendency and range (no median available)
- No dot plot data to extract
- Map to same output schema with `median = null`

### Era B: HTML Primary + PDF Fallback

- 30 of 36 meetings have HTML accessible pages (`fomcprojtabl{DATE}.htm`)
- HTML scraping via BeautifulSoup (already implemented in Phase 3)
- PDF fallback for 6 meetings without HTML
- Extract both Table 1 (projections) and Figure 1 (dot plot)

### Era C: HTML Primary + PDF Fallback

- All 23 meetings have HTML accessible pages
- Same HTML scraping approach as Era B
- PDF contains additional content (individual narratives) extractable for enrichment

## Output Schema

### Projection Table (`sep_projections.parquet`)

| Column | Type | Description |
|--------|------|-------------|
| `meeting_date` | str (YYYYMMDD) | FOMC meeting date |
| `era` | str (A/B/C) | Document format era |
| `variable` | str | `gdp_growth`, `unemployment`, `pce_inflation`, `core_pce`, `fed_funds` |
| `horizon` | str | `current_year`, `year_plus1`, `year_plus2`, `longer_run` |
| `median` | float | Median projection (null for Era A) |
| `ct_low` | float | Central tendency low |
| `ct_high` | float | Central tendency high |
| `range_low` | float | Range low |
| `range_high` | float | Range high |

### Dot Plot (`sep_dot_plot.parquet`)

| Column | Type | Description |
|--------|------|-------------|
| `meeting_date` | str (YYYYMMDD) | FOMC meeting date |
| `horizon` | str | `current_year`, `year_plus1`, `year_plus2`, `longer_run` |
| `rate` | float | Federal funds rate midpoint (%) |
| `num_participants` | int | Number of participants projecting this rate |

*Note: Dot plot data available only for Era B and C meetings (2012-01 onwards).*

### FRED Summary Stats (`fred/sep_all_fred.parquet`)

| Column | Type | Description |
|--------|------|-------------|
| `date` | datetime | FRED observation date |
| `variable` | str | `gdp_growth`, `unemployment`, `pce_inflation`, `core_pce`, `fed_funds` |
| `statistic` | str | `median`, `ct_mid`, `ct_low`, `ct_high`, `range_low`, `range_mid`, `range_high`, `*_lr` variants |
| `fred_id` | str | FRED series ID |
| `value` | float | Projection value (%) |

### Meeting Registry (`sep_meeting_registry.json`)

| Field | Type | Description |
|-------|------|-------------|
| `date` | str (YYYYMMDD) | Meeting date |
| `date_formatted` | str (YYYY-MM-DD) | Human-readable date |
| `year` | int | Year |
| `quarter` | str | Q1-Q4 |
| `has_dot_plot` | bool | True for 2012-01 onwards |
| `html_url` | str/null | URL of HTML accessible page (if available) |
| `pdf_url` | str | URL of PDF document |
| `source` | str | `html+pdf`, `html_minutes+pdf`, `pdf` |
| `era` | str | `A`, `B`, or `C` |

## File Inventory

```
fomc-sep/data/
├── references/              # 70 source PDFs (one per meeting)
├── sep_tables_raw/          # 54 scraped HTML pages
├── fred/                    # FRED API extracts (5 variable files + combined)
├── sep_meeting_registry.json
├── sep_dot_plot.parquet     # 1,448 dot entries (2012-2026)
├── sep_dot_plot.csv
└── sep_table1_raw.parquet   # 160 rows (post-2015 only — needs expansion)
```

## Known Gaps

| Gap | Impact | Resolution |
|-----|--------|-----------|
| Era A Table 1 not yet parsed from PDF | No projection data for 2007-2011 | Phase 4: pdfplumber extraction |
| Era B pre-2015 Table 1 not parsed from HTML | Missing ~12 meetings of projection data | Improve HTML parser for pre-2015 format |
| `era` field not yet in meeting registry | Cannot filter by era | Update registry |
| FRED series only have 3 current-year obs | FRED restructures vintages differently | Use HTML/PDF scrape as primary for current-year |
| Individual participant narratives (Era A, C) not extracted | Missing qualitative context | Future enhancement |
