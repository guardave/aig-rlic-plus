# Ops Otis — aig-rlic-plus PWS

**Identity:** Ops Otis · role=ops (SRE/infra) · `agent:ops-otis`
**Global profile:** `~/.claude/agents/ops-otis/`
**Project PWS:** `_pws/ops-otis/`
**Onboarded to this project:** 2026-06-16

## Scope here
Operations/infra support for the AIG-RLIC+ research portal — local devcontainer tooling, Streamlit Cloud deploy/sync hygiene, MCP server health, Docker, package management. NOT research/econometrics/viz/app content (owned by the domain agents: lead-lesandro, econ-evan, data-dana, viz-vera, research-ray, appdev-ace).

## Environment facts (2026-06-16)
- Devcontainer: Debian GNU/Linux 13 (trixie), x86_64. Package manager = **apt/dpkg**, `sudo` available.
- Working dir: `/workspaces/aig-rlic-plus` (git, branch `fix260613_lead_horizon`).
- MCP server count: 8 (cap 10 — see CLAUDE.md Context Budget).

## Session log
### 2026-06-16
- Installed **tmux 3.5a** via apt (`sudo apt-get install -y tmux`). Pulled in `libjemalloc2`. dpkg stdin warning was cosmetic.
- Initialized Ops Otis identity for this project.

## Outstanding
- (none yet)
