# AIG-RLIC+ — Server / Session Migration Handoff

**Purpose:** everything needed to stand up this project's multi-agent Claude Code sessions on a **new server** and continue without losing state.
**Author:** Lead Lesandro · **Date:** 2026-07-07 · **Repo tip at handoff:** `main` @ `b2da882` (17 pairs).

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
- **Deployment:** production `https://aig-rlic-plus.streamlit.app` tracks `main`; the `dawodev` preview tracks the in-flight branch. **A new pair / new page / render-module change needs a REBOOT** (Manage app → Reboot app), not just a push — Streamlit discovers `app/pages/*.py` and imports render modules at process start (META-FRD file-sync lag). Verify via the Playwright iframe pattern in `scripts/cloud_verify.py` (iframe `title="streamlitApp"`, poll hydration ≤45s).

## 6. Local state to resolve BEFORE the move (working tree)

Working tree is clean of tracked changes and **origin is in sync** (nothing unpushed). `temp/*` is gitignored (probes/screenshots — scratch, correctly not migrating). **Only 3 untracked items are off-GitHub:**
1. `docs/spec_memo_lead_horizon_granularity_20260613.pdf` (197 KB, stakeholder spec memo) — **preserve** (committed with this handoff if approved).
2. `_pws/ops-otis/session-notes.md` (Ops Otis / SRE role PWS) — **preserve**.
3. `_pws/lead-lesandro/lead_horizon_qa/codex_qaudit.log` (2.2 MB Codex/Ivy audit log) — **scratch**; Ivy's actual report is already committed under `_pws/audit-ivy/`. Recommend: copy manually if wanted, else drop (don't bloat the repo). **← the one open decision.**

## 7. Where to resume (open work)

**Open GitHub issues:**
- **#13** — lead-tournament peak vs published-winner lead reads as a report inconsistency on ~12/14 pairs. The fix pattern is piloted on the 3 newest pairs; **roll it out to the ~11 older pairs** + codify as an SOP rule. This is the biggest queued item.
- **#4** — storytelling architecture review (pre-existing).

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
