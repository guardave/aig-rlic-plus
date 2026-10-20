"""Crisis episodes of the Story zoom section (DPS-EP1) and the rule that exempts one: an episode is exempt for a
pair when the indicator has no data over it, i.e. the pair's current-run signals frame starts after the episode
ends (QA cement F2: the series starts in 2005-11, so no dot-com zoom can exist). Rule-based, never a hand-listed
exemption; legacy pairs (no current-run signals frame) are never exempt."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

# canonical episode windows (the zoom producers use these spans or wider ones)
EPISODES = {
    "dotcom": ("Dot-com bust", "2000-03-01", "2002-10-31"),
    "gfc": ("Global financial crisis", "2007-10-01", "2009-06-30"),
    "covid": ("COVID crash", "2020-02-01", "2020-06-30"),
    "inflation_2022": ("Inflation shock and rate hikes", "2022-01-01", "2022-12-31"),
}
NO_DATA_TEXT = "no indicator data for this episode (the indicator's history starts after it)"


def indicator_start(pair_id: str, rdir=None) -> pd.Timestamp | None:
    """First date of the pair's current-run signals frame (Phase B), else None."""
    from components import provenance as P
    rdir = Path(rdir or P.RESULTS / pair_id)
    if not P.is_phase_b(pair_id, rdir):
        return None
    try:
        f = P.current_file(pair_id, "signals", "parquet", rdir)
    except P.CurrentRunFileError:
        return None
    if f is None or not Path(f).exists():
        return None
    try:
        idx = pd.read_parquet(f).index
    except Exception:                                   # noqa: BLE001 - unreadable frame: no exemption
        return None
    return pd.Timestamp(idx.min()) if len(idx) and isinstance(idx, pd.DatetimeIndex) else None


def exempt_episodes(pair_id: str, rdir=None) -> list[str]:
    """Slugs of the episodes that end before the indicator's data begin."""
    start = indicator_start(pair_id, rdir)
    if start is None:
        return []
    return [s for s, (_n, _a, end) in EPISODES.items() if pd.Timestamp(end) < start]
