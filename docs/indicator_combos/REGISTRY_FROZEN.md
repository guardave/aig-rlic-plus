# Registry frozen (Phase 1 closed)

**Date:** 2026-10-17.
**Decision:** the user chose option (a) and the Lead relayed it. The project is now an **exploratory** research
programme. Phase 1 closes as it stands at commit `d780845f`.

## What is frozen

| File | git blob (at d780845f) | sha256 |
|------|------------------------|--------|
| `registry/hypotheses.yaml` | `9dfc0111f17c064f5049c71cabaff3ceb9749c17` | `672fe7cbb92eb1ef969767b149440d3dd26584f535e106119e066e1bd910f955` |
| `registry/families.yaml` | `313e4c8d61fa637c064d405dbbab76884e06651d` | `a4d092107ea0d037db638e3637dc02d4b8783cb2bd171ec3c13c70ead6579af6` |
| `registry/schema.json` | — | `fa7064616401d2b251c67c4ea736705a3d1c236e23f829907fdce170f6ca98b0` |

- Any change to these files after this note is a new version and must be reported as such.
- Phase 2 does not edit them.

## Status of the 9 "discovery-informed prospective" hypotheses

The following hypotheses **stay registered** for evaluation on V-C (the frozen forward log) and V-S (the
sequestered international dataset), whenever that data exists:

| Question | Hypotheses |
|----------|------------|
| D1-01 | H1, H2 |
| D1-02 | H1 |
| D1-05 | H1 |
| D1-27 | H1, H2, H3 |
| D1-28 | H1, H2 |

- **Nobody waits for them.** Phase 2 does not depend on their evaluation.
- **No forward log has been started.** No V-S data has been acquired.
- **Their limits are recorded** in `KNOWN_LIMITS.md`. These are the open points from Codex review 3, which are not
  being fixed.

## What Phase 2 is

Phase 2 is exploratory analysis on the existing point-in-time data. Its outputs are in `phase2/`. Every result is
labelled "Exploratory" and reports:

- the number of tests in its family, and the multiplicity-adjusted result using the method registered in
  `families.yaml`;
- the null-tournament percentile;
- comparisons against buy-and-hold, the best single indicator and the naive composite;
- the sample window and its recession count.

No result carries verdict words.

Running a registered hypothesis on historical data in Phase 2 is **not** a V-C or V-S evaluation. It does not change
the hypothesis's registered status.
