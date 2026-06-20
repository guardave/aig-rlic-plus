# Audit Ivy Experience

## Lead-Horizon Audit Lessons

The lead-horizon reconciliation showed that corruption and artifact claims are testable when the audit keeps three views separate: committed baseline, working-tree state, and proposal/temp outputs.

## Detecting In-Place CSV Corruption

- The corruption signature was a committed tournament CSV whose row count or lead grid differed from the working-tree copy.
- `git show HEAD:results/<pair>/<tournament>.csv` is the correct published-baseline control.
- Row-count, lead-grid, and byte-hash comparison caught whether a working file had been appended or mutated.
- For `indpro_spy`, the committed grid was coarse `[0,1,2,3,6]`; any working copy showing full `L0..12` in the publish-time CSV would have been evidence of in-place append corruption.
- For `umcsent_xlv`, the committed grid was `[0,1,2,3,4,5,6]`; the working copy matched `HEAD`, confirming cleanup.

## Polarity-Mirror Sweep Artifact Pattern

- The cheap lead sweep used a standardized polarity-aware grid, not the native tournament.
- A sweep best can be the positive mirror of a native negative-Sharpe strategy that the native tournament cannot validly promote.
- In the audit, `indpro_spy` sweep `L12 = 1.3744` matched `abs(-1.3744)` from an invalid native row, while the native valid `L12` best was only about `1.0412`.
- Recommendation: use sweep artifacts for exploration only. Promotion decisions require a native tournament rerun over the candidate lead grid.

## Winner Summary Alias Gap

- Several `winner_summary.json` files carried display aliases or registry names that did not literally match raw tournament row codes.
- Sharpe maxima still reconciled, but exact row identity was harder to verify without implicit mapping.
- Recommendation: every winner summary should include raw tournament keys alongside display aliases: raw `signal`, raw `threshold`, raw `strategy`, raw lead column/value, source tournament file, and source row index.

## Recommendations for Future Independent Audits

- Start with `git status --short`, but do not infer baseline truth from the working tree.
- Enumerate committed tournament and winner files via `git ls-tree` and read them through `git show HEAD:`.
- For each pair, report total rows, valid rows, committed lead grid, published winner, max valid row, and match status.
- Hash working tournament files against `HEAD` before inspecting proposal artifacts.
- Recompute headline metrics from returns files using the reported OOS window and show the formula.
- Keep baseline and proposals in separate report sections.
- Flag schema or naming ambiguity as an audit issue even when numeric reconciliation passes.
- Do not repair files during the audit; write findings and let the owning producer team fix root causes.
