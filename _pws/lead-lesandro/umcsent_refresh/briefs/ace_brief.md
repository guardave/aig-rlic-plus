[App Dev Ace] — Mode-3 session dispatch — umcsent_xlv WINNER REFRESH (stage 4, final maker)

You are App Dev Ace. Resolve persona via `./AGENTS.md`: read SOP `docs/agent-sops/appdev-agent-sop.md` + `~/.claude/agents/appdev-ace/`. Lead Lesandro (Claude) is manager + sole checker.

## Context
umcsent_xlv's winner was corrected (Evan) and its narrative rewritten (Ray) — both Lead-verified. The portal CONFIG still quotes the OLD/wrong winner and must be updated to match. Ground truth: corrected `results/umcsent_xlv/winner_summary.json`, Ray's narrative `docs/portal_narrative_umcsent_xlv_20260423.md`, and Ray handoff `_pws/lead-lesandro/umcsent_refresh/ray_handoff.md`.

### CORRECTED winner (use EXACTLY)
- UMCSENT **3-month momentum** (umcsent_mom / S3_mom), rolling **z-score > +1.0** trigger, **6-month lead**, P1 Long/Cash, target XLV.
- OOS Sharpe **1.16**, OOS annual return **+7.95%**, max drawdown **-0.7%**, Calmar **11.3**, Sortino 1.61, vol 6.9%, win rate 16%, turnover 3.29. OOS 2019-04-30→2025-12-31.

## Task — update `app/pair_configs/umcsent_xlv_config.py`
1. Replace every stale winner-specific value with the corrected one. Currently the config quotes **OOS Sharpe 1.02 / +11.93% / max DD -10.9%** and "6-month lead" prose — fix the numbers (1.02→1.16, +11.93%→+7.95%, -10.9%→-0.7%, add Calmar 11.3 where relevant) and ensure the signal is described as **3-month momentum with a rolling z-score>1.0 trigger and a 6-month lead** (the 6-month lead is correct; keep it). Pull headline numbers from `winner_summary.json` — do NOT invent values; mirror Ray's narrative prose/structure.
2. Confirm zero stale tokens remain: `grep -E "1\.02|11\.93|10\.9" app/pair_configs/umcsent_xlv_config.py` returns nothing.
3. Keep the signal-rule / strategy-rule prose consistent with the corrected rule (z-score>1.0 trigger, 6-month lead, Long/Cash).

## Gates
- META-CMP pre-commit gates must pass (T1.1 schema, T1.2 loader smoke — will run since app/ staged, T1.3 filename, T2 chart completeness). Loader smoke confirms the page renders + charts resolve.
- Do NOT touch other pairs. Frozen `hy_ig_v2_spy` untouchable. Do NOT edit Ray's narrative or Evan's results.
- Commit your config change (author App Dev Ace), referencing the umcsent winner refresh.

## Output
- Print `ACE DONE` at line start + the confirming grep (zero stale tokens) + files changed, or `ACE BLOCKED: <reason>`.

Begin now.
