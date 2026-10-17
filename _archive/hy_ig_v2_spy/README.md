# hy_ig_v2_spy (archived)

Retired Sample pair. Pages/results/charts were archived 2026-06-20 (commit 0f9f7724);
its pipeline, chart and retro-fix scripts were moved to `scripts/` here on 2026-10-16.

Why archived: an HMM Sample pipeline (never a live pair). It used a
smoothed full-sample HMM (look-ahead in the regime probability). Superseded by the
causal `hy_ig_spy` rebuild of 2026-10-16. The live pair is `hy_ig_spy`; nothing in
the app depends on the "v2" id.

History is preserved (git mv). Scripts here are not maintained and are not wired
into any lint, registry or gate.
