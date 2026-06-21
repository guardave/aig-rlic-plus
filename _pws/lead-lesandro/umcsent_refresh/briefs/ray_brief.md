[Research Ray] — Mode-3 session dispatch — umcsent_xlv WINNER REFRESH (stage 3)

You are Research Ray. Resolve persona via `./AGENTS.md`: read SOP `docs/agent-sops/research-agent-sop.md` + `~/.claude/agents/research-ray/`. Lead Lesandro (Claude) is manager + sole checker.

## Context — the umcsent_xlv narrative describes a WRONG winner; correct it
winner_summary.json was corrupted and is now fixed (Evan, Lead-verified). The portal **narrative + your owned interpretation_metadata fields still describe the OLD/wrong winner** (Sharpe 1.02, +11.93%, max DD -10.9%). They must be rewritten to the CORRECTED winner. Ground truth = Evan handoff `_pws/lead-lesandro/umcsent_refresh/evan_handoff.md` + corrected `results/umcsent_xlv/winner_summary.json`.

### CORRECTED winner (use these numbers EXACTLY)
- Signal: UMCSENT **3-month momentum** (S3_mom / `umcsent_mom`) — the 3-month change in University of Michigan Consumer Sentiment, NOT the level or YoY.
- Rule: rolling **z-score > +1.0** trigger, **6-month lead**, P1 Long/Cash (long XLV when triggered, else cash).
- Metrics: OOS Sharpe **1.16**, OOS annual return **+7.95%**, max drawdown **-0.7%**, Calmar **11.3**, Sortino 1.61, annual vol 6.9%, win rate 16%, turnover 3.29. OOS 2019-04-30→2025-12-31. Direction: **procyclical** (rising consumer-sentiment momentum → XLV strength over the next ~6 months).

## Task — rewrite the umcsent_xlv narrative to the corrected winner
1. `docs/portal_narrative_umcsent_xlv_*.md` (find the current narrative file): rewrite every winner-specific claim — signal description (3-month momentum + rolling z>1.0, NOT the old framing), the **6-month lead** (this part of the OLD prose was actually right — keep it), and ALL performance numbers (1.16 / +7.95% / -0.7% / Calmar 11.3). Remove every instance of the stale 1.02 / +11.93% / -10.9%.
2. Update your owned interpretation_metadata fields {mechanism, caveats, narrative_summary, expected_direction if needed} to match. Evan already fixed `key_finding`; keep consistent. Do NOT touch Evan/Dana-owned fields.
3. **RES-JFU (binding):** first user-facing use of any technical term/abbrev gets long-form + (abbrev) + plain gloss (e.g. "out-of-sample (OOS) — tested on data not used to pick the rule"; "z-score — how many standard deviations above its recent average").
4. Honest framing: state the mechanism (consumer-sentiment momentum leading the health-care sector by ~6 months) as a hypothesis; carry any confidence/fragility caveats faithfully from winner_summary/evidence_status (do not oversell). The indicator-level evidence (granger/regime/etc.) was NOT regenerated and remains valid — reference it as-is.

## Conventions
- Repo root, project Python. Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. Stay in your lane — do NOT edit Evan's design/results or Ace's config (Ace updates the config next, from your narrative).
- Commit your narrative + metadata changes (author Research Ray). META-CMP gates run on commit.
- Handoff `_pws/lead-lesandro/umcsent_refresh/ray_handoff.md` (sections rewritten + exact corrected numbers for Ace to wire into the config).
- Print `RAY DONE` at line start + files changed, or `RAY BLOCKED: <reason>`.

Begin now.
