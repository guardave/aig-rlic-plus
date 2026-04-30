# AIG-RLIC+

Research dashboard and analysis pipelines for indicator-target economic/market relationships.

## Setup

```bash
pip install -r requirements.txt
```

For full FRED refreshes, set `FRED_API_KEY` in the environment. The devcontainer forwards `FRED_API_KEY` and persists Codex config under `CODEX_HOME=/home/vscode/.codex`.

Note: `pandas-datareader` is installed only on Python versions below 3.14 because the current release is not compatible with Python 3.14 plus pandas 3.x. The pipeline still has `fredapi` and direct FRED CSV fallback paths.

## HY-IG Legacy Archive

Some ICE BofA OAS series on FRED now expose shortened history. Clean checkouts can still run against committed datasets. If you need to rebuild the optional local legacy archive from public Internet Archive captures, review the applicable source terms and run:

```bash
python scripts/fetch_fred_wayback_archive.py --accept-ice-terms
```

The generated files under `data/legacy_fred_archive/` are intentionally ignored by git.
