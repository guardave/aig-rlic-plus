# Archived Documentation & Artifacts

This directory preserves documentation and artifacts from pairs and waves that have been superseded. Files are kept (not deleted) for historical reference, audit trail, and "how we used to do things" comparison.

## Archive Entries

### 2026-04-22 — Wave 10G.1 — `hy_ig_spy` v1 archived

**What:** The original (Feb 2026) HY-IG × SPY implementation (pair_id `hy_ig_spy`, v1).

**Why:** Superseded by `hy_ig_v2_spy` (the "Sample" / canonical reference pair, ratified in Wave 10G.2) and by a fresh `hy_ig_spy` built on the latest SOPs + APP-PT1 templates (Wave 10G.4).

**What was moved:**

| From | To |
|------|-----|
| `results/hy_ig_spy/` | `results/hy_ig_spy_v1/` |
| `data/hy_ig_spy_daily_20000101_20251231.parquet` | `data/hy_ig_spy_v1_daily_20000101_20251231.parquet` |
| `data/hy_ig_spy_daily_latest.parquet` | `data/hy_ig_spy_v1_daily_latest.parquet` |
| `data/data_dictionary_hy_ig_spy_20260228.csv` | `data/data_dictionary_hy_ig_spy_v1_20260228.csv` |
| `scripts/data_pipeline_hy_ig_spy.py` | `scripts/archive/data_pipeline_hy_ig_spy_v1.py` |
| `docs/analysis_brief_hy_ig_spy_20260228.md` | `docs/archive/analysis_brief_hy_ig_spy_v1_20260228.md` |
| `docs/portal_narrative_hy_ig_spy_20260228.md` | `docs/archive/portal_narrative_hy_ig_spy_v1_20260228.md` |
| `docs/research_brief_hy_ig_spy_20260228.md` | `docs/archive/research_brief_hy_ig_spy_v1_20260228.md` |
| `docs/spec_memo_hy_ig_spy_20260228.md` | `docs/archive/spec_memo_hy_ig_spy_v1_20260228.md` |
| `docs/storytelling_arc_hy_ig_spy_20260228.md` | `docs/archive/storytelling_arc_hy_ig_spy_v1_20260228.md` |
| `app/pages/1_hy_ig_story.py` | `app/pages_archive/hy_ig_spy_v1_story.py` |
| `app/pages/2_hy_ig_evidence.py` | `app/pages_archive/hy_ig_spy_v1_evidence.py` |
| `app/pages/3_hy_ig_strategy.py` | `app/pages_archive/hy_ig_spy_v1_strategy.py` |
| `app/pages/4_hy_ig_methodology.py` | `app/pages_archive/hy_ig_spy_v1_methodology.py` |

**Pair registry:** the hardcoded v1 entry in `app/components/pair_registry.py` was removed. The auto-discovery loop now skips any directory ending in `_v1` or `_archived`.

**Current replacement:** `hy_ig_spy` (fresh implementation, Wave 10G.4+) and `hy_ig_v2_spy` (the canonical Sample, ratified under Wave 10G.2 as the quality benchmark all new pairs are compared against).

**Git history:** all moves used `git mv` where files were tracked; the two parquet files in `data/` were gitignored and moved via plain `mv`. History of tracked files follows the rename transparently (`git log --follow`).
