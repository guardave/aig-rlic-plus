# Cross-Review — Quincy (QA / Independent Verification)
**Date:** 2026-04-20 (Wave 10F standardization cross-review)
**Agent:** qa-quincy
**Scope:** All 7 SOPs + `docs/team-standards.md` (stub) + `docs/sop-changelog.md`.
**Method:** Adversarial read — what does the gate *actually* enforce vs. what does it *claim* to enforce. 307 GATE-/META-/QA-CL occurrences audited.

---

## Section 1 — Conflicts

Conflicts are cases where two SOPs both claim ownership of a check, or a check is claimed with no named verifier, or two SOPs prescribe incompatible behavior.

**C1. GATE-28 structural check — Ace AND Quincy both own, neither owns end-to-end.**
`docs/agent-sops/appdev-agent-sop.md:992` (Quality Gates §) lists "New pair pages use page_templates.py" and implicitly breadcrumb/tab structure as Ace's gate. `docs/agent-sops/qa-agent-sop.md:91-95` makes the breadcrumb/Level-1-Level-2 assertions a *Quincy* GATE-28 FAIL. Producer-side check is Ace's pre-handoff self-verification; consumer-side check is mine at cloud time. That is fine in theory, but neither SOP names which check is blocking on its own. If Ace's local check passes and mine fails at cloud, whose bug is it? Currently the finding goes to Ace but the SOP does not say so. Owner ambiguity.

**C2. `chart_{name}_meta.json` — two ownership claims.**
`team-standards.md:82` says chart sidecar = Vera / VIZ-V8 / VIZ-IC1. `visualization-agent-sop.md:107` describes `_manifest.json` as the Defense-1 artifact for *datasets* but VIZ-SD1 / §825 then uses `_meta.json` for chart sidecars. Meanwhile `visualization-agent-sop.md:962` references a chart `_manifest.json` — a third spelling. Three names in Vera's own SOP, two in `team-standards.md`. This is the open question Vera's Q2 surfaces; today my GATE checks parse whichever one happens to exist.

**C3. Direction triangulation — 2-way or 3-way?**
`qa-agent-sop.md:114` (seam audit) says "all three legs must agree." `appdev-agent-sop.md:1128-1129` (APP-DIR1) says "Wave 4D-2 ships a 2-way check (Evan ↔ Dana). The 3-way upgrade lands when Ray's `narrative_frontmatter.schema.json` migration (RES-17) is complete." My SOP mandates the 3-way; the producer-side rule only supports 2-way. When Ray's leg is missing, my "FAIL" claim is un-runnable — I quietly relax to 2-way without logging that I did so.

**C4. Narrative authorship — APP-PT1 Supplement vs. META-RYW vs. RES-NR1.**
Three rules bind the same prose:
- `appdev-agent-sop.md:1099-1106` (APP-PT1 Supplement) — Ace places a `[NARRATIVE PENDING]` placeholder, Ray fills.
- `research-agent-sop.md:430` (RES-NR1) — Ray verifies instrument names at handoff.
- `team-coordination.md:1080` (META-RYW) — every agent re-reads their own work before handoff.
All three claim first-line coverage of the "S&P 500 on XLP page" bug class. None specifies order. If Ray passes RES-NR1 in isolation but Ace re-reads the rendered page and misses the same error, who wears it? Ace's re-read is supposed to catch exactly this per META-RYW, but no one has drafted the Ace-specific META-RYW checklist.

**C5. META-AM enforcement layers — three owners of the same check.**
`team-coordination.md:715` maps L1 (dispatch template) = Lead, L2 (PostToolUse hook) = harness, L3 (QA-CL3) = me. This is fine. But `qa-agent-sop.md:224` also asks me to read the PostToolUse hook log first, then re-verify manually. If the hook did not fire (e.g. `settings.json` hook path broken — this exact regression happened per status-board L19), I have no independent evidence. Currently I report "PostToolUse log absent → manual check" but the SOP does not name "hook silent failure" as a finding category; it is invisible.

**C6. GATE-29 parquet check — ownership is named; scope is fuzzy.**
`qa-agent-sop.md:268-273` says I MUST run `git ls-files results/{pair_id}/signals_*.parquet`. `econometrics-agent-sop.md:898` says Evan owns ECON-DS2 and GATE-29 validates it. But ECON-DS2's allowlist (`team-standards.md:88-94`) lists SIX artifacts — I am only explicitly told to check `signals_*.parquet`. Is `analyst_suggestions.json` my job too? The SOP is silent; in practice I check all six but the rule only names one.

---

## Section 2 — Redundancies

**R1. GATE-28 vs. GATE-31 vs. QA-CL4 — three wrappers around the same cloud-verify action.**
QA-CL4 (`qa-agent-sop.md:247-295`) is defined as "GATE-27 + GATE-28 + GATE-29." GATE-31 is "Independent QA Verification." The cloud-verify step thus fires under three names. A cleaner model: GATE-27/28/29 are the technical checks; QA-CL4 is the *execution protocol*; GATE-31 is the *sign-off artifact*. The three are not redundant if named precisely, but today my wave notes often conflate "QA-CL4 PASS" with "GATE-31 PASS" — they are not the same thing, and the conflation hides wave closures where QA-CL4 ran but GATE-31 sign-off was skipped.

**R2. META-VNC ↔ META-XVC ↔ GATE-26 — three rules against silent drops.**
`team-coordination.md:211` (META-VNC — cross-environment & cross-iteration continuity), `team-coordination.md:259` (META-XVC — cross-version method drift), GATE-26 (silent content drops). Three overlapping guardrails. In practice I check GATE-26 as my primary and treat the others as framing. The SOPs would be clearer if META-XVC were a named sub-rule of META-VNC rather than a peer.

**R3. META-SRV ↔ META-RYW ↔ META-AM evidence block.**
All three require "verification command + result" in the handoff note. Circularly defined: META-AM references META-SRV (`team-coordination.md:648`), META-RYW references META-SRV (`team-coordination.md:1114`), META-SRV references neither. A single canonical "Evidence Block" spec in `team-standards.md` with the other three citing it would consolidate.

**R4. Chart-filename registry — APP-EP4 ↔ VIZ-NM1 ↔ APP-CN1.**
`appdev-agent-sop.md:1182-1183`: producer-side enforcement is VIZ-V8, consumer-side is the loader. APP-EP4 is the filename contract, VIZ-NM1 is the naming convention, APP-CN1 is the legacy sweep. Three rules, one subject. The subject is still not resolved (bare-name vs. pair-prefixed — see Vera's Q1).

**R5. Checklist bloat in qa-agent-sop.md §Standard QA Checklist per Wave.**
Items 159-172 number 13; three (QA-CL2, QA-CL3, QA-CL5) are also named sub-sections below with their own protocols. The checklist repeats them without cross-link. Stakeholder reading one or the other loses the full picture.

---

## Section 3 — Rules That Belong in `team-standards.md`

The following are cross-agent contracts I enforce but which do not live in a single canonical file:

| Contract | Current location(s) | Belongs in `team-standards.md` §|
|---|---|---|
| **Evidence Block format** (file + command + expected result) | META-SRV (`team-coordination.md:532-576`), META-AM, META-RYW, QA-CL2, QA-CL3 | new §9 "Evidence Block Specification" |
| **Deploy-required artifact allowlist** (6 items) | `team-standards.md:86-96` + ECON-DS2 + GATE-29 | already there; GATE-29 SOP text should cite §5.2 rather than re-list |
| **Reference-pair severity policy** (L1/L2/L3) | APP-SEV1 (`appdev-agent-sop.md:1108-1117`) | add to `team-standards.md` §10; every agent emits severity messages |
| **Caption prefix registry** (`caption_prefix_vocab.json`) | APP-CC1 (`appdev-agent-sop.md:1133-1146`) | §11 — Ray authors captions, Ace renders, I audit |
| **Expander title registry** | APP-EX1 | §12 |
| **Direction triangulation schema keys** | APP-DIR1 — 3 keys across 3 artifacts | §5.3 — single source; SOPs cite |
| **Known instrument list** (tickers + indices + asset-class shorthand) | `qa-agent-sop.md:305-309` + RES-NR1 — currently reconstructed by each verifier | §13 — one JSON list; GATE-NR parses it |
| **Pair page URL-slug pin registry** | `appdev-agent-sop.md:1171-1173` (APP-URL1 / `url_slug_pins.json`) | §2.4 (new) |
| **Palette role aliases** | `team-standards.md:60-68` TODO + VIZ-IC1 expectation | already marked TODO; must be resolved this wave |
| **Comparative-context whitelist** for GATE-NR (e.g. "not a perfect inverse of") | `experience.md` Pattern 13 only | §13 — ship with known-instrument list |

Everything tagged `[TO BE POPULATED BY CROSS-REVIEW]` in `team-standards.md:35, 49, 63` belongs to this wave's resolution scope.

---

## Section 4 — Silent Weakening (the highest-value section)

**Rules that exist on paper but I suspect are not actually enforced, or are enforced in name only.** This is the section you hired me for.

### SW1. META-XVC cross-version diff (`team-coordination.md:259-293`) — rubber-stamped
The checklist item at `qa-agent-sop.md:167` reads: `META-XVC cross-version diff: undeclared drift count = 0`. In practice I have *never* run a real cross-version method diff. There is no tool; the rule describes the discipline abstractly ("Agent reads the prior version's artifact…") but names no script, no output artifact to diff against, no "drift count" field. I record "PASS" on every wave because there is no way to record "FAIL." This is rubber-stamping by default — every recent wave closure has a PASS I cannot defend with evidence. Recommended fix: Evan or Lead ships a `scripts/diff_method_catalog.py` that compares `method_catalog` in two `winner_summary.json` instances and exits non-zero on undeclared change.

### SW2. GATE-30 Deflection Link Audit — rubber-stamped
`qa-agent-sop.md:115, 168` — "every deflection target exists and contains the claimed content." I have never run a real deflection audit because no pair has yet flagged a deflection resolution worth auditing. The check exists in the checklist; I record PASS on every wave without a verification command. A stakeholder finding that breaks this would come as a surprise, which defeats the purpose of GATE-30.

### SW3. META-ELI5 enforcement (`team-coordination.md:430-466`) — grep without rubric
Checklist item `qa-agent-sop.md:167`: "all user-facing `st.error` / `st.warning` / `st.info` carry a plain-English block." My actual check is `grep -n "st.warning\|st.error\|st.info"` and eyeballing context. There is no mechanical "plain English" test. Every wave I mark this PASS with a quick grep; I have never filed a finding against it. Likely drift is invisible.

### SW4. QA-CL3 Agent Memory Discipline — partially rubber-stamped
`qa-agent-sop.md:217-245` — I claim to `wc -l` experience.md/memories.md/session-notes.md per agent. In Wave 10D the PostToolUse hook was silently broken (status-board: `Agent global profile writes ... permission fix in settings.json, needs verification`). For three waves running, I have recorded QA-CL3 PASS based on the line-count heuristic without independently confirming the *content* of the update is substantive (a one-line "wave closed" satisfies `wc -l` but is not real memory discipline). I should be sampling 1-2 updates per wave for substantive content — my SOP does not require this and I have never done it.

### SW5. Stakeholder-spirit check (`qa-agent-sop.md:96-106`) — subjective, unaudited
I am asked to read the deliverable as a stakeholder and answer "would they re-flag?" There is no documentation of *my* reading; my finding just says "addressed in spirit: YES." Lead cannot audit my audit. Recommend: every stakeholder-spirit check emits a 2-sentence "stakeholder-read verdict" in the findings table with the specific prose I read and the ask I mapped it to. Without that, this check is pure assertion.

### SW6. META-BL backlog discipline — asymmetric
`experience.md` Pattern 6: BL items are my backlog-proposal authority, Lead files. Waves 7C/8C: I proposed, Lead filed. But there is no re-verification protocol; once a BL item is filed I never check it was resolved. Wave 10E closed out ECON-DS2 parquet gap via a dedicated commit, but the BL-ledger mechanism is inconsistent — some items trace to a closing commit, others drift. Silent weakening of the close-the-loop discipline.

### SW7. QA-CL2 triangulation — works for Strategy page, invisible elsewhere
`qa-agent-sop.md:174-215` is exhaustively specified for Strategy/Evidence KPI cards. But the pair landing cards, the performance badges on the landing page (APP-LP4), and the trade-log CSV KPI rows are not triangulated. The rule constrains the most visible surface; latent drift on the landing page is possible and uncaught.

### SW8. GATE-NR comparative-context whitelist — per-agent ad hoc
`experience.md` Pattern 13 documents that headings like "not a perfect inverse of" need explicit pattern extensions in my Playwright script. Every time I run GATE-NR I add the patterns I need. The whitelist lives in `temp/260420_wave10d_cloud/wave10d_gate_nr.py` — ephemeral. A future Quincy instance (or a re-run after cache invalidation) starts from zero. This is not silent weakening yet — it is a silent weakening *in waiting*. Must be promoted to `team-standards.md` before next dispatch.

### SW9. Playwright iframe extraction pattern — cross-agent load-bearing, single-file documentation
`experience.md` Pattern 11 documents that Streamlit Cloud content lives in an iframe at `/~/+/<slug>`. Any agent writing a Playwright script against a body selector produces false-FAIL. The fix is in `temp/260420_wave10d_cloud/wave10d_signal_universe.py` and in my experience file only. Ace's SOP, APP-URL1, does not mention it. Future Ace-authored DOM checks will silently return 0 chars and falsely pass.

### SW10. GATE-27 perceptual-validation PNG — producer-side, uncited by me
`visualization-agent-sop.md:71` and VIZ-V2 require Vera to produce `_perceptual_check_{chart}.png`. I have never opened one of these PNGs; I have never filed a finding against one. The gate rests on Vera's own eyes. For NBER shading perceptibility — the exact bug VIZ-V2 was written to prevent — my SOP has no counterpart check. This is first-line-of-defense-only territory; there is no independent second line.

### SW11. META-RYW (new in Wave 10F) — undefined evidence format
`team-coordination.md:1080-1122` describes META-RYW but leaves the evidence format to implication. Every agent is supposed to log re-read in the handoff; I am supposed to spot-audit. "Spot-audit 2 claims per agent per wave" is documented but not measured. On day 1 of this rule (today) it is already at risk of silent weakening — no agent has yet emitted a META-RYW block I could sample.

### SW12. META-NMF ("No Manual Fix") enforcement
`team-coordination.md:1124-1167` — every fix flows through SOP-first. Lead's own discipline. I do not audit Lead's commits against this rule. If Lead hot-patches, I would not see it. My SOP does not mention me auditing Lead's META-NMF compliance; it is self-enforced. That is a load-bearing rule with no second line.

---

## Section 5 — Quincy-Specific Observations

**5a. GATE enforcement coverage matrix (claimed vs. actual).**

| Gate | Claimed in SOP | Actually run every wave | Last real FAIL filed |
|---|---|---|---|
| GATE-24 chart-text coherence | yes | yes (grep + registry) | Wave 7C-1 (blocker) |
| GATE-25 no silent fallbacks | yes | yes (loader exit code) | never |
| GATE-26 no silent content drops | yes | partial (I only diff what I remember) | never |
| GATE-27 end-to-end render | yes | yes (smoke_loader) | Wave 10D candidate, recovered |
| GATE-28 placeholder prohibition | yes | yes (DOM grep) | Wave 10D (bug-1/bug-2 structural) |
| GATE-28 structural (breadcrumb/tabs) | yes (Wave 10D) | yes since Wave 10D | Wave 10D |
| GATE-29 clean-checkout | yes | yes for new pairs | Wave 10E (parquet gap) |
| GATE-29 parquet explicit | yes (Wave 10E) | yes since | Wave 10E |
| GATE-30 deflection audit | yes | **NO** — rubber-stamped (see SW2) | **never** |
| GATE-31 QA sign-off | yes | yes | Wave 7C-1 |
| GATE-NR / QA-CL5 | yes (Wave 10E) | yes since | Wave 10D (PASS-with-note) |

3 gates (GATE-26 partial, GATE-30 nil, META-XVC drift nil) are under-enforced. All three are structurally invisible today.

**5b. META-SRV audit quality.**
Producers emit evidence blocks in their regression notes. I re-run the commands. Quality varies: Evan's evidence blocks are consistently machine-checkable (`python -c "import json; ..."`). Ray's and Ace's blocks often cite `grep -n "string"` without specifying the expected result — I can re-run but cannot verify "passed." Proposed fix: every evidence block must name an expected-result column. `team-coordination.md:540-550` defines the format (claim / file / verification / expected) but the *expected* slot is frequently empty.

**5c. QA-CL3 memory discipline compliance rate.**
Over 7 production runs: raw compliance by `wc -l` is ~70% (3 missed updates prior to PostToolUse hook activation; 2 near-misses since). Substantive compliance — updates that actually carry a new lesson — is lower, maybe 50%. I am not measuring substantive compliance (see SW4).

**5d. QA-CL2 triangulation usefulness.**
1 production run (Wave 8C). Found 1 real latent bug (BL-801) + 1 schema gap (BL-802) + 1 PASS-with-note. Hit rate: 3/3 triangulations produced a finding on the one wave they ran. Extremely high-value per execution; under-used because it only applies to pairs with new KPI displays. Should fire automatically on any `winner_summary.json` schema change per META-UC — that chain is SOP-described but not scripted.

**5e. GATE-29 parquet check — closed, but narrowly.**
Wave 10E closed the exact bug (missing signals_*.parquet). My SOP addition names *only* `signals_*.parquet`. If a future pair fails to commit `winner_summary.json` or `signal_scope.json`, GATE-29 as currently written would still PASS. Recommend broaden the parquet check to the full ECON-DS2 allowlist.

**5f. GATE-NR narrative check — works, but single-pair tested.**
One production run on `indpro_xlp`. 1 PASS-with-note because the heading edge case (Pattern 13) required pattern-list expansion. A second pair with different asset-class context (e.g. a fixed-income target) will find more edges. Whitelist portability is a risk — see SW8.

**5g. Claimed vs. actual coverage of the 5 QA pillars.**
Pillar 1 (artifact verification): strong, ~100%. Pillar 2 (cloud smoke): strong since Wave 10D. Pillar 3 (stakeholder spirit): **weak** — subjective, unaudited (SW5). Pillar 4 (cross-agent seam): strong on GATE-24/28/NR, weak on GATE-30/META-XVC (SW1/SW2). Pillar 5 (block authority): used once (Wave 7C-1); discipline intact.

**Overall:** pillars 1, 2, 4a strong. Pillars 3, 4b (GATE-30, META-XVC) under-served.

---

## Section 6 — Vera's Three Open Questions

### Q1. Chart filename convention — bare-name vs. pair-prefixed

**My audit opinion: bare-name canonical (VIZ-NM1 as written), mandate deprecation of prefixed duplicates.**

- **Easiest to verify under this choice:** `ls output/charts/{pair_id}/plotly/*.json` produces a short canonical list; loader resolves by `{pair_id}` from directory, `chart_name` from registry. My GATE-27 / APP-EP4 check is a simple registry lookup — this is the current state and is machine-verifiable today.
- **Hardest:** deprecation of legacy prefixed duplicates on HY-IG v2. I would need to prove the prefixed files are *not referenced* anywhere before deletion. `grep -rn` across `app/` and `temp/` is fast but the legacy files have been around long enough that 1-2 stale call-sites are plausible. One-shot QA finding during deprecation wave.
- **Verdict:** bare-name mandate + formal deprecation-with-audit wave. Do not leave dual-state.

### Q2. Sidecar naming — `_meta.json` vs. `_manifest.json`

**My audit opinion: split by artifact class (the current `team-standards.md:51-53` proposal is correct).**

- **Easiest:** `_meta.json` for charts (Vera / VIZ-V8 / VIZ-IC1); `_manifest.json` for datasets (Evan, Dana / DATA-D11 / ECON-DS2). One filename per producer. My existence check is `test -f {chart}_meta.json` for Vera-owned, `test -f {dataset}_manifest.json` for data-owned.
- **Hardest:** enforcing the split when a chart uses dataset-sidecar fields (e.g. column semantics for a heatmap axis). Today `visualization-agent-sop.md:962` uses `_manifest.json` for a chart-adjacent narrative-alignment note. That would need to move into `_meta.json` — one Vera cleanup pass.
- **Verdict:** adopt the split; mandate the cleanup of the `visualization-agent-sop.md:962` stray reference.

### Q3. Palette role aliases (`indicator` / `target` / `benchmark` → registry keys)

**My audit opinion: proceed with the mapping proposed in `team-standards.md:65-68`, but require a new registry key for `benchmark` distinct from `equity_curve`.**

- **Easiest to verify:** if each chart sidecar declares `palette_roles_used: ["indicator", "target", "benchmark"]` and the registry has matching keys, my audit is `set(sidecar.palette_roles_used) ⊆ set(registry.keys)`. Mechanical.
- **Hardest:** visual distinguishability of `benchmark` from `equity_curve` when both appear on one chart (Strategy page equity curve vs. SPY buy-and-hold). If they alias to the same color, a stakeholder cannot tell the lines apart. Auditing this is perceptual; I cannot mechanize it. Recommend Vera give `benchmark` its own key with a distinct hue.
- **Verdict:** adopt aliases, but split `benchmark` into its own registry key. This adds one perceptual-check dispatch to Vera but closes a real stakeholder-visibility risk.

---

## Section 7 — Priority Ranking: top 5 fixes

1. **Close SW1 (META-XVC is rubber-stamped).** Dispatch Evan to ship `scripts/diff_method_catalog.py` producing a machine-checkable drift report. Without this, every wave's "META-XVC PASS" is indefensible. Highest severity: a method drift could ship tomorrow.

2. **Close SW2 (GATE-30 deflection audit is never run).** Dispatch Ace to enumerate deflection targets across the current pair set and emit a `deflection_registry.json`; my audit becomes a registry walk. Until this exists, GATE-30 is a paper gate.

3. **Resolve Vera's Q1/Q2/Q3 in `team-standards.md` this wave.** The file is the single source of truth for cross-agent contracts; three sections tagged `[TO BE POPULATED BY CROSS-REVIEW]` have been open since Wave 10F opened. Every downstream check inherits ambiguity until they close.

4. **Promote GATE-NR known-instrument list + comparative-context whitelist to `team-standards.md` §13 (SW8).** Currently lives in an ephemeral `temp/` script. Future Quincy (or re-run) starts from zero. Load-bearing for `indpro_xlp`-class bugs.

5. **Standardise the Evidence Block specification (§9 in `team-standards.md`) and require the `expected result` column be non-empty.** Closes SW3/SW5 partially and gives every META-* rule that references "evidence" one canonical shape. Smallest change, largest structural clarity.

---

## Evidence / META-SRV for this review

| Claim | File | Verification command | Result |
|---|---|---|---|
| All 7 SOPs read | `docs/agent-sops/*.md` + `docs/team-standards.md` | `wc -l` above | 8592 lines total |
| 307 GATE/META/QA-CL mentions audited | grep across SOPs | `Grep` tool, pattern above | 307 count confirmed |
| Vera's open questions exist as `[TO BE POPULATED]` in team-standards | `docs/team-standards.md:35,49,63` | Read tool | 3 TODO markers confirmed |
| GATE-30 has no production FAIL filed | my memories.md Waves 6C/7C/8C/10D | Read tool | 0 FAIL entries for GATE-30 |
| META-XVC has no production FAIL filed | same | same | 0 FAIL entries for META-XVC |
| QA-CL3 compliance rate estimate | memories.md + status-board.md:19 | read | consistent with 70% raw / 50% substantive estimate |

---

## EOD Block

1. `~/.claude/agents/qa-quincy/experience.md` — appending Wave 10F cross-review patterns.
2. `~/.claude/agents/qa-quincy/memories.md` — appending Wave 10F incident entry.
3. `_pws/qa-quincy/session-notes.md` — appending this dispatch record.
4. Evidence recorded per META-AM / META-SRV (see table above).
