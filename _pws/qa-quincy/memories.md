# Quincy — PWS Memories (fallback when global sandbox denies write)

**Context:** Known recurring sandbox issue on `~/.claude/agents/*/memories.md` — Ace and Vera both hit it this wave (Wave 10H.1). Lead is aware. Entries below are mirror-writes intended for future promotion to `~/.claude/agents/qa-quincy/memories.md` once sandbox permits.

---

## Wave 10H.1 — Canonical cloud_verify.py + Hibernation Blocker (2026-04-22)

**Context:** Dispatched to (A) promote `temp/260422_wave10g_full/focused_verify.py` to canonical `scripts/cloud_verify.py` with Pattern 22 fix + APP-PT2 Sample Methodology check + backward-compat regression gate; (B) run verify on deployed app post-Ace-`e6767e0` + Vera-`c9f4d47`; (C) record VIZ-O1 + GATE-28 + APP-PT2 + QA-CL2 verdicts.

**Results:**
- **A:** DONE. `scripts/cloud_verify.py` landed. Key additions beyond the temp source: configurable `--base`/`--out`, focus-pair × page grid, post-iframe 30s hydration poll, 3 unique ELI5 markers hardcoded (from Vera's `narrative_alignment_note` strings) for APP-PT2, landing-page raw-column-leak check, `results.json`+`summary.txt` outputs, exit code 0/1.
- **B:** BLOCKED. 17/17 FAIL (`no_iframe`) across 2 runs. Diagnostic probe showed `TITLE: AIG-RLIC+ Research Portal · Streamlit` but `BODY: "Hosted with Streamlit / Created by guardave"` (42 chars). Classic Pattern 19/20 hibernating-deployment signature. Did not retry in tight loop per dispatch; escalated to Lead for user reboot.
- **C VIZ-O1:** 65/65 focus-pair sidecars PASS (Vera's backfill clean). **35 sidecars missing on 6 legacy pairs** (dff_ted_spy, indpro_spy, permit_spy, sofr_ted_spy, ted_spliced_spy, vix_vix3m_spy). Vera pre-flagged these as "no sidecar-writing function to patch" follow-up refactor. Non-blocking for 10H.1 closure; proposed backlog item BL-VIZ-O1-LEGACY.
- **C GATE-28 + APP-PT2 live:** BLOCKED until reboot. Regression gate structurally safe by data shape — only `hy_ig_v2_spy` has the `exploratory_charts` key in `analyst_suggestions.json`.
- **C QA-CL2:** T3 = N/A per new P2 continuous-rebalancing exception (hy_ig_spy). T1/T2 unchanged from Wave 10G.4F.

**Key lesson — Pattern 22 fix is retained, not re-derived.** The promotion from `temp/` to `scripts/` is a **clean rewrite**, not a `git mv`. That forces an explicit audit of which behaviours are canonical (Pattern 22, iframe detection, check_page) vs. which are wave-specific (the hardcoded slug list, the scratch output dir name). The canonical script should be wave-agnostic; wave-specific assertions (like APP-PT2's 3 ELI5 markers) live inline but are clearly labelled.

**Key lesson — Hibernation is distinguishable from stale-deployment by the body-stub signature.** Both Pattern 19 (stale code served) and hibernation (no code served) return identical `no_iframe` on the verify script. The diagnostic probe (`temp/warmup_probe.py`) disambiguates in ~10s by checking outer body text: "Hosted with Streamlit / Created by guardave" = hibernation; a page with error tracebacks or prefix-pending paths = stale code. **Do this probe before escalating** — hibernation needs a user reboot; stale code sometimes needs a fresh push to trigger redeploy.

**Key lesson — Out-of-scope VIZ-O1 failures are not Wave-closure blockers when pre-documented by the owning agent.** Vera's handoff explicitly carved out 4 legacy generators as follow-up refactor. Finding 35 missing sidecars in exactly those pair directories confirms the documented gap rather than surfaces a surprise bug. Correct triage: log as backlog for Wave 10H.2/10I, do NOT block 10H.1 closure. The test for "pre-documented vs. surprise" is whether the upstream handoff called it out in writing — it did.

**Sandbox note (meta):** Attempted global `Edit` on `~/.claude/agents/qa-quincy/memories.md` denied. Mirrored here per META-AM fallback protocol (same path Ace and Vera took this wave). Lead dispatch doc acknowledges this as a recurring issue.

*Wave 10H.1 added. Production runs: 13.*
