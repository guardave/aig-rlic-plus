# AIG-RLIC+ — Server / Session Migration Handoff

**Purpose:** everything needed to stand up this project's multi-agent Claude Code sessions on a **new server** and continue without losing state.
**Author:** Lead Lesandro · **Date:** 2026-07-07 · **Repo tip at handoff:** `main` @ `b2da882` (17 pairs).
**Active work branch (GH #13 rollout):** `feat260707_lead_coherence_rollout` (pushed to origin) — see §7.1 for full resume state. Switch into the devcontainer, `git checkout feat260707_lead_coherence_rollout`, and start at §7.1.

---

## 0. TL;DR — do these in order on the new server

1. `git clone https://github.com/guardave/aig-rlic-plus.git` → **everything committed is on GitHub and origin is in sync** (verified 0 ahead / 0 behind at handoff).
2. `git config core.hooksPath scripts/hooks` — **re-arm the pre-commit gates** (they do not travel with a clone).
3. Re-supply the **secrets & home-dir state that are NOT in the repo** (§3). This is the part that actually breaks if skipped.
4. Verify: `python3 scripts/validate_all_schemas.py` → `pairs=17 fail=0`; `streamlit run app/app.py` renders the 17-pair landing grid.

---

## 1. Repo state (all on GitHub)

- **`main` @ `b2da882`**, `origin` = `https://github.com/guardave/aig-rlic-plus.git`, in sync.
- **17 registered pairs.** Newest three: `cass_freight_spy` (coincident/null), `eci_total_comp_spy` (first **quarterly** pair; lagging), `wells_fargo_housing_spy` (lagging/reverse-dominant).
- **Branches kept (both unmerged, intentional):** `explore_pair_prescreen` (pair-prescreen discussion artifact), `fix260613_lead_horizon` (suspended spec-memo). Everything else is merged and deleted.
- **`data/Data Master.xlsx` IS git-tracked** (20 MB) — it is the source for non-FRED indicators (e.g. Wells Fargo HMI, after FRED delisted NAHB). It travels via GitHub; no manual copy needed.

## 2. Environment the new server must provide

- **Nested devcontainer.** `bwrap` fails here → every `codex`/`codex exec` call MUST pass `--dangerously-bypass-approvals-and-sandbox`. (The devcontainer *is* the sandbox.)
- **Tooling:** Python 3 stack (numpy/pandas/scipy/statsmodels/linearmodels/arch/scikit-learn/plotly/matplotlib/openpyxl/jsonschema/playwright), **Streamlit 1.54.0**, **`codex` CLI** (needs its own login), **`gh` CLI** (auth to GitHub account `guardave`), **tmux** (for Codex/Ivy dispatch), **Playwright + chromium** (cloud/local verify).
- **Git identity for Lead commits:** `--author="Lead Lesandro <lead-lesandro@idficient.com>"`, and every commit message ends with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`. Agents never commit — they defer git to Lead (LEAD-DL1).
- **Pre-commit gates** (via `scripts/hooks`, armed with `git config core.hooksPath scripts/hooks`): T1.1 schema (`validate_all_schemas.py`), T1.3 filename lint, T2 chart-completeness (`lint_chart_completeness.py`), T1.2 loader smoke. Never bypass with `--no-verify` past a gate (META-NMF: fix the producer, not the artifact).

## 3. State & secrets that are NOT in the repo (migrate these manually)

| Item | Location (this server) | Notes |
|---|---|---|
| **Project auto-memory (28 files)** | `~/.claude/projects/-workspaces-aig-rlic-plus/memory/` (+ `MEMORY.md` index) | **Lives in HOME, not the repo.** Copy the whole dir or the accumulated lessons are lost (viz-correctness rules, dispatch policies, deployment gotchas, pair lessons). Highest-value non-repo asset. |
| **Shared agent context** | CLAUDE.md expects `~/.agents/` (`core/`, `playbooks/`, `profiles/`, `knowledge/`) | On THIS server `~/.claude/agents/<role>` symlinks point to **`/home/david/.agents/profiles/`** which is **not mounted** (the symlinks are broken — global-profile reads/writes fail here). On the new server, provision a real `~/.agents/` (or fix the symlink target) so profiles resolve. Project-local SOPs in `docs/agent-sops/` are the working fallback and DO travel via git. |
| **MCP servers + API keys** | `.claude/settings.json` / `.claude/settings.local.json` (+ shell env) | 8 MCP servers (fred, yahoo-finance, alpha-vantage, financial-datasets, filesystem, context7, sequential-thinking, memory). **FRED and Alpha-Vantage need API keys**; re-supply on the new server. `financial-datasets` uses mcp-remote. Keep MCP count ≤10 (context budget). |
| **Codex CLI session** | `~/.codex/config.toml` (+ login) | `trust_level="trusted"`. Re-login on the new server; verify with `codex exec --dangerously-bypass-approvals-and-sandbox 'say hi'`. |
| **gh CLI auth** | `~/.config/gh/hosts.yml` | Re-auth to account `guardave` (needed for `gh issue`/PR). |

## 4. The team & operating model (so a fresh session behaves correctly)

**Personas** (SOPs in `docs/agent-sops/`, dispatched by Lead as subagents; each resolves persona via `./CLAUDE.md` / `./AGENTS.md`):
- **Lead Lesandro** — coordinator; the only one who does git; holds merge authority requests.
- **Data Dana** — pulls/validates data, Phase-0 gate, classification.
- **Econ Evan** — econometrics + tournament, winner provenance (ECON-T5), lead analysis.
- **Viz Vera** — the Plotly chart set (data-integrity: chart == data).
- **Research/Narrative Ray** — the Story/Evidence/Strategy/Methodology prose (honest, data-coupled).
- **App Dev Ace** — Streamlit config + pages + registry wiring.
- **Audit Ivy (`audit-ivy`)** — standing INDEPENDENT Codex-backed QA auditor (PWS `_pws/audit-ivy/`), dispatched via tmux for trust reconciliation.

**Load-bearing rules (do not drop across the migration):**
- **LEAD-MA1** — merges to `main` require **explicit user authorization** each time (an auto-mode classifier also blocks unauthorized production merges).
- **LEAD-DL1** — Lead dispatches; agents do the work and defer all git to Lead; Lead never hand-edits agent-owned files.
- **META-NMF** — every fix = fix the producer/SOP first, never patch the rendered artifact; never `--no-verify` past a gate.
- **feedback_gh_issues_over_backlog** — new findings/deferred work → **GitHub issues**, not backlog rows.
- **Stage commits explicitly** (never `git add -A`) — 3 known untracked scratch items live in the tree (see §6).

## 5. Pair-build pipeline & deployment (how work actually gets done)

- **New pair = 5 phases**, each Lead-gated: Dana (data/Phase-0) → Evan (tournament/econometrics) → Vera (charts) → Ace (portal config+pages) → Ray (narrative). Freshest **monthly** template: `cass_freight_spy`; **quarterly** template: `eci_total_comp_spy`. Mirror an existing pair's artifact shapes exactly.
- **GH #13 lead-chart pattern is native for new pairs** (winner's own Sharpe-by-lead curve foregrounded, cross-signal envelope as context) — Evan emits `lead_winner_curve` + `lead_clean_envelope` CSVs; Vera builds the coherent chart.
- **Deployment:** production `https://aig-rlic-plus.streamlit.app` tracks `main`; the preview apps `aig-rlic-plus-dev01` / `aig-rlic-plus-dev02` track the in-flight branch (dawodev retired 2026-07-07; **no repoint** — a new app instance is spun up per branch). **A new pair / new page / render-module change needs a REBOOT** (Manage app → Reboot app), not just a push — Streamlit discovers `app/pages/*.py` and imports render modules at process start (META-FRD file-sync lag). Verify via the Playwright iframe pattern in `scripts/cloud_verify.py` (iframe `title="streamlitApp"`, poll hydration ≤45s).

## 6. Local state to resolve BEFORE the move (working tree)

**As of the GH #13 session (2026-07-07 PM):** active branch `feat260707_lead_coherence_rollout` is pushed and in sync. ~~**DO NOT COMMIT `.venv`**~~ — **RESOLVED 2026-07-15** (commit `a6a04cec`): `.venv` is now gitignored and untracked (`git rm -r --cached .venv`, 5,583 files). Files remain on disk. Note this did **not** shrink `.git` (~398 MB) — `.venv` is still in history; reclaiming that needs a `filter-repo` rewrite plus a force-push, which is a separate decision.

~~Also `requirements.txt` is missing `pyarrow`, `kaleido`, `playwright` (needed by pipelines/verify). The devcontainer provides these natively, so the env is a non-issue there.~~ — **CORRECTION, 2026-07-15.** The observation was right; the conclusion was **false and actively misleading**. The devcontainer never provided these natively. They (plus `streamlit`) had been hand-`pip install`ed into the running container, so they lived only in the container filesystem — the 2026-07-15 rebuild destroyed all four, leaving the app, the META-CMP pre-commit gates, and `cloud_verify.py` broken until they were reinstalled by hand. **Resolved:** they are now declared in `requirements-dev.txt` and installed by `setup.sh` at build (kept out of `requirements.txt`, which is the Streamlit Cloud deploy manifest — see that file's header for the per-package rationale).

**Lesson:** "the devcontainer provides it" is only true of something declared in `requirements.txt`, `setup.sh`, or a devcontainer feature. Anything hand-installed into a running container is invisible to a rebuild and will vanish without warning.

Original migration note (still valid): Working tree is otherwise clean of tracked changes and **origin is in sync** (nothing unpushed). `temp/*` is gitignored (probes/screenshots — scratch, correctly not migrating). **Only 3 untracked items are off-GitHub:**
1. `docs/spec_memo_lead_horizon_granularity_20260613.pdf` (197 KB, stakeholder spec memo) — **preserve** (committed with this handoff if approved).
2. `_pws/ops-otis/session-notes.md` (Ops Otis / SRE role PWS) — **preserve**.
3. `_pws/lead-lesandro/lead_horizon_qa/codex_qaudit.log` (2.2 MB Codex/Ivy audit log) — **scratch**; Ivy's actual report is already committed under `_pws/audit-ivy/`. Recommend: copy manually if wanted, else drop (don't bloat the repo). **← the one open decision.**

## 7. Where to resume (open work)

**Open GitHub issues:**
- **#13** — IN PROGRESS on `feat260707_lead_coherence_rollout`. **See §7.1 for the full state, design decisions, triage, and resume steps.** The rollout evolved well beyond the original "apply the pilot to 11 pairs" — it is now a single-source-of-truth refactor with a governed re-selection workflow.
- **#4** — storytelling architecture review (pre-existing).

### 7.1 GH #13 lead-coherence rollout — resume state (branch `feat260707_lead_coherence_rollout`)

**The core reframe (why this grew).** The `lead_sharpe_distribution` chart drew its bars from the **exploratory sweep** (`lead_horizon_sweep.py`, contiguous L0–12, a DIFFERENT P1/P2 grid) while the **strategy-tournament details** and winner selection come from the pair's **native tournament** (`tournament_results_*.csv`, a COARSE lead set, e.g. ISM `{1,2,3,6,12}`). Two differently-computed sources side by side = a trust break. **Fix = one source of truth per pair:** extend the native tournament to the full grid with an engine that reproduces it exactly, and project BOTH the lead chart and the strategy details from that one table.

**Design decisions locked with the stakeholder (do not re-litigate):**
- **One SoT per pair at its NATIVE frequency.** Monthly pairs → monthly L0–12. Daily pairs (Class A) → daily-lead axis; **do NOT resample daily→monthly** (that creates a second tournament with a different winner than the deployed daily strategy).
- **Always L0–12** for monthly; **include L0**, labelled *coincident* (lookahead; real-time floor is usually L1 given publication lag).
- **Patching missing leads CAN force a winner re-selection** (completing the grid changes the selection universe). This is an **ECON-T5 event**, not a chart fix: if a patched lead beats the frozen winner, re-run natively, adjudicate via the full T3/T5 cascade (durability/bootstrap — may keep or change the winner), **propagate to every downstream artifact + narrative**, then run the consistency scan. Winner selection stays tied to the run's grid; patched leads are provenance-tagged (`pipeline` vs `patched`).

**Tooling built this session (all pure pandas/numpy, NO LLM in the pipeline — portable for non-Claude devs):**
- `scripts/refresh_lead_coherence_artifacts.py` — extends a pair's native tournament to the full grid; emits `lead_tournament_native_{date}.csv` (the SoT), `lead_winner_curve`, `lead_clean_envelope`; patches the manifest. **4 safety gates:** reconcile (winner Sharpe vs winner_summary), fidelity (per-combo vs tournament_results ≥98%), coherence (envelope ≥ winner), **governance (ECON-T5: blocks silent winner change)**. `--screen` = re-selection triage without writing. Adapters build the work frame from the signals parquet + `strategy_returns.bh_return`.
- `scripts/generate_lead_charts.py` — shared builder now emits the **coherent chart** (winner's own curve + envelope, solid=pipeline / open=patched markers) when the artifacts exist; falls back to the sweep chart otherwise. PNG export is best-effort (won't block JSON if kaleido absent).
- `scripts/gate_viz_lead.py` — **GATE-VIZ-LEAD** (coherence + single-source consistency enforcement).
- `scripts/gate_consistency.py` — **GATE-CONSISTENCY** (cross-artifact winner scanner: winner is the max clean valid combo, kpis/lead-curve/narrative all agree). **Baseline: 0 hard failures / 18 pairs** — current published state is internally consistent.
- Scope memo: `docs/spec_memo_gh13_lead_coherence_rollout_20260707.md` (original plan; partly superseded by the single-source pivot above).

**Triage verdicts** (100% reconcile where a verdict is given — trustworthy):
| Pair(s) | Verdict | Action |
|---|---|---|
| **ism_services_spy, m2sl_yoy_spy** | STABLE (winner is global max on full grid) | **DONE** — coherent chart + corrected narrative + both gates green (committed) |
| **busloans_spy** | RE-SELECTS (`contraction/…/L11 = 1.6159 > 1.4999`) | **maker native re-run** + ECON-T5 adjudication + propagate |
| **petrol_inv_spy** | RE-SELECTS (L11 `1.5273 > 1.4779`) | **maker native re-run** + propagate |
| **umcsent_xlv** | engine can't reproduce (diff threshold template, no lookback col) | **maker native derive** |
| **indpro_spy** | engine can't (parquet lacks S1_level/S4_dev_trend cols) | **maker native derive** for the coherent chart (winner already full-grid) |
| **indpro_xlp** | engine can't (reconcile 0.60 vs 1.33, diff template) | **maker native derive** (winner already full-grid) |
| **gold_copper_xli, hy_ig_spy, vix_vix3m_spy, phlxsox_spy** | Class A / T3 (daily) | daily-lead-axis presentation, separate track |

**Role & topology (LEAD-DL1).** Lead Lesandro is **manager + checker — NOT the maker.** Stakeholder ruled out Lead-as-maker (⇒ Modes 2 & 5 are out). Intended topology is **Mode 3: Lead dispatches Codex makers; Lead ratifies.** The native re-runs / native-derive are **Codex maker work**; Lead ratifies each with GATE-VIZ-LEAD + GATE-CONSISTENCY + cloud-DOM verify.

**Resume steps in the devcontainer:**
1. `git checkout feat260707_lead_coherence_rollout` (env is native there — no Otis/venv concerns).
2. **Checker:** point a preview app (dev01/dev02) at this branch, then cloud-verify the two done pairs: `python scripts/cloud_verify.py --base https://aig-rlic-plus-dev01.streamlit.app --pairs ism_services_spy,m2sl_yoy_spy`.
3. **Manager:** draft + dispatch the Codex maker brief (via the `codex` skill, Mode 3) for **busloans, petrol** (re-selection) then **umcsent, indpro_spy, indpro_xlp** (native derive). Brief = native re-run at L0–12 → adjudicate ECON-T5 → regenerate ALL downstream + narrative → hand back. **Ratify** each via both gates + DOM before it's "done."
4. **Class A / T3 daily** pairs: separate design (daily-lead chart + "traded daily / monthly sweep is a diagnostic" framing).
5. Codify the pattern as an SOP rule (VIZ-LEAD + the single-source-of-truth principle) once the fleet is converted.

**Candidate GH issues not yet filed** (per gh-issues-over-backlog):
- Annotated Statistical-Methods examples bake numbers from 4 pair snapshots (hy_ig/gold_copper/indpro/phlxsox) → add periodic "example-number vs source-chart" re-verification (drift guard).
- Template registry-JSON sync bug (guarded on wrong key; Dana fixed forward in the cass producer — audit older pairs).
- `generate_strategy_perf_charts.py` CAGR-vs-arithmetic annualization convention mismatch (fleet-wide).
- OOS-vs-full-sample drawdown-window: shared producer pattern; audit all pairs' drawdown charts.
- Bare `except: pass` in `page_templates._load_winner_summary` swallows schema drift.
- Registry-walk compliance gate (assert every registered pair carries selection + lead blocks) — 3 out-of-band pairs have landed on main mid-branch historically.

**Tooling debt:**
- Cloud-probe tab selector: Streamlit changed tab markup → `button[role="tab"]` returns 0; use `div[data-testid="stTabs"] button`. Fold into `scripts/cloud_verify.py`.
- `cloud_verify.py` per-tab screenshot-click times out on hidden sub-tab handles (skip non-visible handles).

**Next prospective pairs:** `data/prospective_pairs.csv` (priority order).

---
_Generated as a migration handoff. The single most important non-repo asset to carry over is the `~/.claude/projects/-workspaces-aig-rlic-plus/memory/` directory — the team's accumulated lessons live there, not in the repo._
