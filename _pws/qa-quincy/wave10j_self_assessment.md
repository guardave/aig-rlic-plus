# Wave 10J Self-Assessment — QA Quincy

**Date:** 2026-04-24  
**Authored by:** QA Quincy (qa-quincy)  
**Purpose:** Honest retrospective before beginning Wave 10J work

---

## 1. Mistakes I Made in Waves 10I.A and 10I.C That I Should Have Caught Myself

### Wave 10I.A — The False-PASS Incident

**What happened:** I ran `scripts/cloud_verify.py`, saw "41/41 PASS" in the summary, and signed off without reading the DOM text files. The DOM files for `dff_ted_spy_strategy.txt`, `sofr_ted_spy_strategy.txt`, and `ted_spliced_spy_strategy.txt` contained the string "Probability engine panel cannot render: No signals_*.parquet under /mount/src/aig-rlic-plus/results/dff_ted_spy". The user found this red banner manually.

**Mistakes I should have caught before handoff:**

1. **GATE-29 was not run.** The SOP explicitly requires `git ls-files results/{pair_id}/signals_*.parquet` before the browser pass for every wave with new pairs. I did not run this. The missing parquet files would have been a hard FAIL before I ever opened the browser. This is not a subtle omission — GATE-29 was added specifically for this class of bug (Wave 10E incident) and is documented in QA-CL4 and in GATE-29's own section. I simply did not do it.

2. **I declared sign-off without reading DOM files.** The DOM text files were captured and written to disk. I did not open them. The script's `ERR_PATS` check never catches `APP_SEV1` banner strings (these are not Python exception class names). I knew this was the script's limitation — it is documented in the script's own header comment. I should have read the files anyway. I did not.

3. **I treated "script PASS = QA PASS."** This is the fundamental category error. The script gathers evidence. I provide the judgment. No judgment was provided.

### Wave 10I.C — HABIT-QA1 Added Only After Escalation

**What happened:** After the false-PASS was flagged by the user, I ran an adversarial audit in Wave 10I.C that found 20 FAILs in the same DOM files I had previously signed off as 41/41 PASS. I then added HABIT-QA1 to the SOP and APP_SEV1_PATS to `cloud_verify.py`.

**Mistakes:**
- HABIT-QA1 should have been a rule I followed implicitly from the beginning of my role — "read the evidence files you just generated before signing off" is not an advanced QA technique. It is basic discipline.
- The rule was only formalized after user escalation, not after my own retrospective. I did not proactively diagnose the failure mode; the user had to call it out.
- GATE-29 mandatory parquet check had already been added to the SOP (Wave 10E incident, documented in QA-CL4 GATE-29 section). I missed it not because the SOP was unclear, but because I did not re-read my own SOP at SOD.

---

## 2. What My SOP Said I Should Do That I Did Not Do

| SOP Requirement | Wave 10I.A Compliance |
|---|---|
| GATE-29: `git ls-files results/{pair_id}/signals_*.parquet` before browser pass | **NOT DONE** |
| QA-CL4 execution protocol step 3: "Run GATE-29 clean-checkout test for every new pair" | **NOT DONE** |
| Reflection & Memory item 1: "What claim pattern nearly slipped through?" | **NOT DONE — skipped reflection entirely** |
| Anti-pattern: "Never sign off without reading DOM text (HABIT-QA1)" | HABIT-QA1 did not exist as a written rule; but the spirit — read your evidence before signing — was implicit and I violated it |
| Standard QA Checklist: "QA-CL4 — Cloud / deploy verification passes (GATE-27 + GATE-28 + GATE-29)" | GATE-27 and GATE-28 were run; **GATE-29 was skipped** |

The SOP was clear on GATE-29. QA-CL4 explicitly lists all three gates. The Wave 10E parquet-preflight addition is documented with a "Root cause" note pointing to exactly this failure mode. I cannot attribute the omission to ambiguity.

---

## 3. What I Learned, and Whether It Is Accurately Recorded in experience.md

**Patterns 25–27** were added to experience.md during Wave 10I.C self-diagnosis:

- **Pattern 25:** APP-SEV1 soft-error banners are not Python exceptions — ERR_PATS will never catch them. ✅ Recorded.
- **Pattern 26:** GATE-29 parquet pre-flight is mandatory before browser pass for every wave with new pairs. ✅ Recorded.
- **Pattern 27 / HABIT-QA1:** Script PASS is evidence-gathering, not verdict — DOM files must be read before sign-off. ✅ Recorded.

**Gaps in experience.md that I need to address now:**

1. **The meta-lesson about SOP compliance:** The incident was not caused by a gap in the SOP. The SOP had GATE-29. I did not follow it. My experience.md records the *technical* lessons (what the check is, why it matters) but does not record the *process failure* lesson: **checking your own SOP at SOD is non-negotiable.** If I had re-read QA-CL4 before starting Wave 10I.A, I would have seen GATE-29 listed explicitly. I am adding this as Pattern 28.

2. **HABIT-QA1 does not yet require reading Evidence page DOM files specifically.** The current HABIT-QA1 rule says "read strategy page DOM text files." Evidence pages are where new cross-period sections (ECON-CP1/CP2, VIZ-CP1) will live. A future false-PASS on Evidence pages would be the same failure mode, different page type. This gap is addressed in Part 3 below.

**Action taken:** Updating experience.md with Pattern 28 as part of this wave.

---

## Summary Verdict on My Own Performance

Wave 10I.A was a genuine QA failure, not a near-miss. Three pairs shipped to production with visible red error banners. The root cause was mechanical: I skipped a required gate (GATE-29) and treated a script's output as a verdict rather than as evidence. The correct response is not "the script wasn't good enough" — the script was doing its job. I was not doing mine.

HABIT-QA1 and the APP_SEV1_PATS additions are the correct remediation. But the deeper fix is personal: re-read the SOP checklist at the start of every verify run, not just at SOD. QA-CL4 is a checklist with three explicit gates. Treating it as a reference document rather than an execution checklist is how GATE-29 gets skipped.

---

*Written: 2026-04-24. Wave 10J.*
