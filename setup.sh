#!/usr/bin/env bash
# ============================================================================
# AIG-RLIC+ Environment Setup
# Quantitative & Qualitative Economic/Financial Analysis Toolkit
# ============================================================================
set -euo pipefail

echo "=========================================="
echo " AIG-RLIC+ Environment Setup"
echo "=========================================="

# --------------------------------------------------------------------------
# 0. Prerequisites — ensure Node.js is available for MCP servers
# --------------------------------------------------------------------------
echo ""
echo "[1/5] Checking Node.js..."

if command -v node &>/dev/null; then
  echo "  -> Node.js $(node --version) found."
else
  echo "  -> Node.js not found. Installing via nvm..."
  export NVM_DIR="${NVM_DIR:-/usr/local/share/nvm}"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
    nvm install --lts
    echo "  -> Node.js $(node --version) installed via nvm."
  else
    echo "  -> nvm not found. Installing nvm + Node.js LTS..."
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.4/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    . "$NVM_DIR/nvm.sh"
    nvm install --lts
    echo "  -> Node.js $(node --version) installed via fresh nvm."
  fi
fi

# --------------------------------------------------------------------------
# 1. Python packages
# --------------------------------------------------------------------------
echo ""
echo "[2/5] Installing Python packages..."

if [ -f "requirements.txt" ]; then
  pip install --quiet -r requirements.txt
else
  pip install --quiet \
    numpy pandas scipy statsmodels scikit-learn \
    matplotlib seaborn plotly \
    yfinance fredapi \
    arch linearmodels \
    jupyterlab ipykernel \
    openpyxl xlsxwriter \
    requests beautifulsoup4 lxml \
    tabulate rich
fi

echo "  -> Python packages installed."

# --------------------------------------------------------------------------
# 2. MCP Servers
# --------------------------------------------------------------------------
echo ""
echo "[3/5] Configuring MCP servers..."

# Tier 1 — No API keys required
claude mcp add financial-datasets -- npx @financial-datasets/mcp-server
claude mcp add yahoo-finance -- npx yahoo-finance-mcp
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
claude mcp add filesystem -- npx @anthropic/mcp-filesystem "$WORKSPACE_DIR"

# Tier 2 — Require API keys (env → interactive prompt → skip)
ALPHAVANTAGE_API_KEY="${ALPHAVANTAGE_API_KEY:-}"
FRED_API_KEY="${FRED_API_KEY:-}"

# Prompt for missing keys if running interactively
if [ -t 0 ]; then
  if [ -z "$ALPHAVANTAGE_API_KEY" ]; then
    echo ""
    echo "  Alpha Vantage API key not found in environment."
    echo "  Get a free key at: https://www.alphavantage.co/support/#api-key"
    read -rp "  Enter Alpha Vantage API key (or press Enter to skip): " ALPHAVANTAGE_API_KEY
  fi
  if [ -z "$FRED_API_KEY" ]; then
    echo ""
    echo "  FRED API key not found in environment."
    echo "  Get a free key at: https://fred.stlouisfed.org/docs/api/api_key.html"
    read -rp "  Enter FRED API key (or press Enter to skip): " FRED_API_KEY
  fi
fi

if [ -n "$ALPHAVANTAGE_API_KEY" ]; then
  claude mcp add alpha-vantage \
    -e ALPHA_VANTAGE_API_KEY="$ALPHAVANTAGE_API_KEY" \
    -- npx @anthropic/mcp-remote https://mcp.alphavantage.co/sse
  echo "  -> Alpha Vantage configured."
else
  echo "  -> Alpha Vantage skipped (no API key)."
fi

if [ -n "$FRED_API_KEY" ]; then
  claude mcp add fred \
    -e FRED_API_KEY="$FRED_API_KEY" \
    -- npx -y fred-mcp-server
  echo "  -> FRED configured."
else
  echo "  -> FRED skipped (no API key)."
fi

# Tier 3 — Reasoning, docs, persistence, web
claude mcp add context7 -- npx -y @upstash/context7-mcp@latest
claude mcp add sequential-thinking -- npx -y @modelcontextprotocol/server-sequential-thinking
claude mcp add memory -- npx -y @modelcontextprotocol/server-memory
claude mcp add fetch -- npx -y @modelcontextprotocol/server-fetch

echo "  -> MCP servers configured."

# --------------------------------------------------------------------------
# 3. Agent Teams
# --------------------------------------------------------------------------
echo ""
echo "[4/5] Enabling agent teams..."

SETTINGS_FILE="$HOME/.claude/settings.json"
mkdir -p "$(dirname "$SETTINGS_FILE")"

if [ -f "$SETTINGS_FILE" ]; then
  # Merge the env key into existing settings using Python
  python3 -c "
import json, sys
with open('$SETTINGS_FILE') as f:
    data = json.load(f)
data.setdefault('env', {})['CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS'] = '1'
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
else
  echo '{"env":{"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS":"1"}}' | python3 -m json.tool > "$SETTINGS_FILE"
fi

echo "  -> Agent teams enabled."

# --------------------------------------------------------------------------
# 4. Verification
# --------------------------------------------------------------------------
echo ""
echo "[5/5] Verifying installation..."

echo ""
echo "  Node.js:"
if command -v node &>/dev/null; then
  echo "  OK  node $(node --version)"
  echo "  OK  npx  $(npx --version)"
else
  echo "  FAIL node not found"
fi

echo ""
echo "  Python packages:"
python3 -c "
packages = [
    ('numpy',        'numpy'),
    ('pandas',       'pandas'),
    ('scipy',        'scipy'),
    ('statsmodels',  'statsmodels'),
    ('scikit-learn', 'sklearn'),
    ('arch',         'arch'),
    ('linearmodels', 'linearmodels'),
    ('matplotlib',   'matplotlib'),
    ('seaborn',      'seaborn'),
    ('plotly',       'plotly'),
    ('yfinance',     'yfinance'),
    ('fredapi',      'fredapi'),
]
ok, fail = 0, 0
for name, mod in packages:
    try:
        m = __import__(mod)
        ver = getattr(m, '__version__', '?')
        print(f'  OK  {name:20s} {ver}')
        ok += 1
    except ImportError as e:
        print(f'  FAIL {name:20s} {e}')
        fail += 1
print(f'\n  {ok} passed, {fail} failed')
"

echo ""
echo "  MCP servers:"
claude mcp list 2>/dev/null || echo "  (could not list — claude may need restart)"

# --------------------------------------------------------------------------
# Done
# --------------------------------------------------------------------------
echo ""
echo "=========================================="
echo " Setup complete."
echo " Restart Claude Code to activate MCP servers."
echo "=========================================="
echo ""
echo " Usage:"
echo "   ALPHAVANTAGE_API_KEY=xxx FRED_API_KEY=yyy bash setup.sh"
echo ""
