# Outstanding work — Lead Lesandro

Last updated: 2026-05-27 EOD.

## Active branch: `fix260526`

Preview app: `https://aig-rlic-plus-fix260526.streamlit.app/`

### Done this session (W0 → W2 of 4 waves)

| Wave | Pair / Scope | Issues | Commits | Cloud verified |
|---|---|---|---|---|
| W0 | template (all 11 pairs) | #23 #34 #104 | `33f78fc` | ✅ 33/33 PASS |
| W0.5 | indpro_spy + vix_vix3m_spy | N1–N7 (missing artefacts) | `a19e7f2` | ✅ |
| W1 | indpro_xlp | #24 #25-1 #25-2 #26 #27 #28 #35 #36 #37 | `24aa35f`, `a9ad54e` | ✅ 0 errors |
| W2 | indpro_spy + cross-pair Granger/sub-period | #63 #64 #65 #66 #67 #68 + bonus | `3718fc9` | ✅ 0 errors |

### Pending next session

1. **W3 — `vix_vix3m_spy` (4 narrative additions):**
   - #60 VIX term-structure explanation
   - #61 "short-term vs medium-term panic" framing
   - #62 inline footnotes for contango / backwardation / hedging demand / put demand / option pricing theory
   - #103 extend Correlation Analysis explanation
2. **Final cross-pair regression** — deep_inspect on all 11 active pairs to confirm W0 + W2 cross-cutting changes didn't regress the 8 pairs not directly targeted.
3. **Cross-pair audit (post-W1 finding)** — grep all pair chart producers for `valid_strats.iloc[0]` / similar `iloc[0]` winner picks; replace with `winner_summary.json` reads (APP-WS1).
4. **Branch close:** merge `fix260526` → `main`; promote `temp/fix260526/relnote.md` to a non-gitignored path; decide whether to keep or delete the preview app.

### Open user-facing questions for next session

- After Cloud picks up tomorrow's commits, user may want to spot-check W1/W2 pair pages personally before final regression.
- Confirm W3 should ship as text-only (no chart producer changes for `vix_vix3m_spy`).
- Decide treatment of `indpro_spy` issue #69 (content request: "who are the team members") — currently marked OUT OF SCOPE; user may want to address separately.

### Broader cross-project tracking

- `scripts/w0p5_generate_missing_strategy_artefacts.py` and the deep_inspect pattern in `temp/fix260526/deep_inspect.py` are good candidates for promotion to project-level tooling (`scripts/` or `app/_smoke_tests/`) at branch close. Currently they live as fix-branch artefacts.
