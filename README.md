# Webull OpenAPI Skill

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

AI agent skill for [Webull OpenAPI](https://developer.webull.com) — enables AI assistants to trade stocks, options, futures, crypto, and event contracts, query market data, and manage accounts via CLI.

Built on the official [webull-openapi-python-sdk](https://github.com/webull-inc/webull-openapi-python-sdk). Supports US, HK, and JP regions with configurable risk controls.

---

## ⚠️ Disclaimer

The information provided by this tool is for reference only and does not constitute investment advice. Trading involves risk; please make decisions carefully.

See [DISCLAIMER.md](DISCLAIMER.md) for the full disclaimer.

---

## Features

- **Multi-Region Support** — US, HK, and JP regions with region-specific order types, trading sessions, and validation
- **Market Data** — Real-time snapshots, tick data, quotes (depth), footprint, and OHLCV bars for stocks, futures, crypto, and event contracts
- **Trading** — Place, modify, cancel orders for stocks, options, futures, crypto, and event contracts
- **Combo Orders** — OTO, OCO, OTOCO combo orders (US only)
- **Option Strategies** — Multi-leg option strategies: vertical, straddle, strangle, butterfly, condor, etc. (US only)
- **Algo Orders** — TWAP, VWAP, POV algorithmic orders (US only)
- **Risk Controls** — Market-specific notional limits (USD/HKD/CNH), quantity limits, symbol whitelist
- **Auto Account Resolution** — Automatically selects the correct account based on asset type
- **Audit Logging** — All order operations are logged for compliance
- **2FA Support** — Interactive authentication flow for accounts with Two-Factor Authentication
- **Region-Aware Disclaimer** — Output includes region-appropriate disclaimer (English for US/JP, trilingual for HK)

---

## Example Prompts

Here are some prompts you can use with your AI assistant:

**Market Data**
- Show me AAPL's daily bars for the last 5 days
- Get a real-time snapshot for AAPL, MSFT, and GOOGL
- What's the current bid/ask for TSLA?

**Account & Portfolio**
- What's my account balance and buying power?
- Show me all my current positions
- List all my linked accounts

**Stock Trading**
- Place a limit order to buy 100 shares of AAPL at $250
- Place a market order to sell 50 shares of TSLA
- Short 10 shares of NVDA at $120

**Options Trading**
- Buy 1 AAPL call option, strike $250, expiring 2026-04-17, limit price $5.00

**Order Management**
- Show me my order history for the last 7 days
- Cancel order with ID abc123

---

## Prerequisites

1. **Webull Developer Account** — Register at:
   - US: [developer.webull.com](https://developer.webull.com/apis/home)
   - HK: [developer.webull.hk](https://developer.webull.hk/apis/home)
   - JP: [developer.webull.co.jp](https://developer.webull.co.jp/apis/home)
2. **API Credentials** — Obtain your `App Key` and `App Secret`
3. **Market Data Subscription** — Subscribe to quotes for market data access:
   - US: [webullapp.com/quote](https://www.webullapp.com/quote) | [Guide](https://developer.webull.com/apis/docs/market-data-api/subscribe-quotes)
   - HK: [webullapp.hk/quote](https://www.webullapp.hk/quote) | [Guide](https://developer.webull.hk/apis/docs/market-data-api/subscribe-quotes)
   - JP: [webull.co.jp/pricing](https://www.webull.co.jp/pricing) | [Guide](https://developer.webull.co.jp/apis/docs/market-data-api/subscribe-quotes)
4. **Python 3.10+**

---

## Installation

```bash
git clone https://github.com/webull-inc/webull-openapi-skills.git
cd webull-openapi-skills

# Create and activate a virtual environment (recommended)
# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt):
python -m venv .venv
.venv\Scripts\activate.bat

# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install the package
pip install -e .
```

Or with dev dependencies:

```bash
pip install -e ".[dev]"
```

> **Why a virtual environment?** It ensures `pip install` and the `webull-skill` command use the same Python interpreter. Without it, `python3` on your system may point to a different version than the one `pip` installs into, causing `ModuleNotFoundError`.

---

## Quick Start

### 1. Configure Credentials

```bash
cp .env.example .env
# Edit .env — fill in WEBULL_APP_KEY and WEBULL_APP_SECRET
# For Webull Japan, also set: WEBULL_REGION_ID=jp
```

> To keep credentials outside the project directory, set `WEBULL_CONFIG_DIR` to any path (e.g. `~/.config/webull-skill`) and place your `.env` there.

### 2. Authenticate (when token is missing or expired)

```bash
webull-skill auth
# Approve the 2FA request in your Webull mobile app
```

### 3. Use It

```bash
# List accounts
webull-skill trading --action account-list

# Stock snapshot
webull-skill market-data --action stock-snapshot --symbols AAPL,TSLA

# Place an order
webull-skill trading --action place --account-id <id> \
  --order-json '{"symbol":"AAPL","side":"BUY","order_type":"LIMIT","limit_price":"180","quantity":"10","instrument_type":"EQUITY","market":"US","time_in_force":"DAY","entrust_type":"QTY","support_trading_session":"CORE","combo_type":"NORMAL"}'
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `WEBULL_APP_KEY` | App Key (required) | — |
| `WEBULL_APP_SECRET` | App Secret (required) | — |
| `WEBULL_ENVIRONMENT` | `uat` (sandbox) or `prod` | `uat` |
| `WEBULL_REGION_ID` | `us`, `hk`, or `jp` | `us` |
| `WEBULL_MAX_ORDER_NOTIONAL_USD` | Max order value for US market (USD) | `10000` |
| `WEBULL_MAX_ORDER_NOTIONAL_HKD` | Max order value for HK market (HKD) | `80000` |
| `WEBULL_MAX_ORDER_NOTIONAL_CNH` | Max order value for CN market (CNH) | `70000` |
| `WEBULL_MAX_ORDER_NOTIONAL_JPY` | Max order value for JP market (JPY) | `1500000` |
| `WEBULL_MAX_ORDER_QUANTITY` | Max order quantity | `1000` |
| `WEBULL_SYMBOL_WHITELIST` | Allowed symbols (comma-separated) | (no restriction) |
| `WEBULL_CONFIG_DIR` | Custom config directory for `.env` and token files | (none) |
| `WEBULL_TOKEN_DIR` | Token storage directory | `<project_root>/conf/` |
| `WEBULL_AUDIT_LOG_FILE` | Audit log file path | stderr only |
| `WEBULL_LOG_LEVEL` | SDK log level | `WARNING` |

> **Note:** `WEBULL_REGION_ID=us` represents **Webull US** ([developer.webull.com](https://developer.webull.com/apis/home)), `WEBULL_REGION_ID=hk` represents **Webull Hong Kong** ([developer.webull.hk](https://developer.webull.hk/apis/home)), and `WEBULL_REGION_ID=jp` represents **Webull Japan** ([developer.webull.co.jp](https://developer.webull.co.jp/api-doc/)).

### Region Configuration Examples

US sandbox:
```env
WEBULL_ENVIRONMENT=uat
WEBULL_REGION_ID=us
```

HK sandbox:
```env
WEBULL_ENVIRONMENT=uat
WEBULL_REGION_ID=hk
```

JP sandbox:
```env
WEBULL_ENVIRONMENT=uat
WEBULL_REGION_ID=jp
```

See [.env.example](.env.example) for the full configuration template.

---

## Available Actions

### Market Data

| Category | Actions | Region |
|----------|---------|--------|
| **Stock** | `stock-snapshot`, `stock-bars`, `stock-batch-bars`, `stock-tick`, `stock-quotes`, `stock-footprint` | US, HK, JP |
| **Futures** | `futures-snapshot`, `futures-bars`, `futures-tick`, `futures-depth`, `futures-footprint` | US |
| **Crypto** | `crypto-snapshot`, `crypto-bars` | US |
| **Event** | `event-snapshot`, `event-depth`, `event-bars`, `event-tick` | US |
| **Screener** | `stock-gainers-losers`, `stock-most-active` | US, HK, JP |
| **Watchlist** | `watchlist-list`, `watchlist-create`, `watchlist-delete`, `watchlist-update`, `watchlist-instruments-list`, `watchlist-instruments-add`, `watchlist-instruments-remove`, `watchlist-instruments-update` | US, HK, JP |

### Trading

| Category | Actions | Region |
|----------|---------|--------|
| **Account** | `account-list` | US, HK, JP |
| **Assets** | `balance`, `position`, `position-detail` (position details by instrument, JP only) | US, HK, JP |
| **Instrument** | `instrument-stock`, `instrument-crypto`, `instrument-futures-products`, `instrument-futures-list`, `instrument-futures-by-code`, `instrument-event-series`, `instrument-event-list`, `instrument-event-categories`, `instrument-event-events` | varies |
| **Stock Order** | `place`, `preview`, `replace` | US, HK, JP |
| **Combo Order** | `batch-place` (OTO/OCO/OTOCO) | US |
| **Option Order** | `option-place`, `option-preview`, `option-replace`, `option-strategy-place` | US, HK |
| **Algo Order** | `algo-place` (TWAP/VWAP/POV) | US |
| **Futures Order** | `futures-place`, `futures-replace` | US |
| **Crypto Order** | `crypto-place` | US |
| **Event Order** | `event-place`, `event-replace` | US |
| **Order Mgmt** | `cancel`, `open`, `history`, `detail`, `local-check` | US, HK, JP |

### Region Differences

| Feature | US | HK | JP |
|---------|:--:|:--:|:--:|
| Stock Trading | ✅ | ✅ | ✅ |
| Option Trading | ✅ | ✅ | ❌ |
| Futures Trading | ✅ | ❌ | ❌ |
| Crypto Trading | ✅ | ❌ | ❌ |
| Event Contracts | ✅ | ❌ | ❌ |
| Combo Orders | ✅ | ❌ | ❌ |
| Option Strategies | ✅ | ❌ | ❌ |
| Algo Orders | ✅ | ❌ | ❌ |
| Order Markets | US | US, HK, CN | US, JP |
| Instrument Categories | US_STOCK, US_ETF | US/HK/CN stock categories | US_STOCK, US_ETF |

### JP Configuration And Order Fields

Set the region in `.env`:
```env
WEBULL_REGION_ID=jp
WEBULL_ENVIRONMENT=uat
```

JP support is intentionally stock-focused:

| Area | JP Support |
|------|------------|
| Market data | Stock actions only: `stock-snapshot`, `stock-bars`, `stock-batch-bars`, `stock-tick`, `stock-quotes`, `stock-footprint` |
| Instrument categories | `US_STOCK`, `US_ETF` |
| Order markets | `US`, `JP` |
| JP market order types | `LIMIT`, `MARKET` |
| US market order types in JP region | `LIMIT`, `MARKET`, `STOP_LOSS`, `STOP_LOSS_LIMIT` |
| JP market time in force | `DAY` |
| US market time in force in JP region | `DAY`, `GTC` |
| Trading sessions | `CORE`, `ALL`, `NIGHT`, `ALL_DAY` |
| Stock account types | `CASH`, `US_MARGIN` |
| JP-only asset action | `position-detail` |

JP stock orders require `account_tax_type`. Margin-specific fields are only valid for `US_MARGIN` accounts:

| Field | Required | Values / Rules |
|-------|----------|----------------|
| `account_tax_type` | Yes for JP stock `place` / `preview` | `GENERAL`, `SPECIFIC` |
| `margin_type` | Margin account only | `ONE_DAY`, `INDEFINITE` |
| `position_intent` | Margin account only | `BUY_TO_OPEN`, `BUY_TO_CLOSE`, `SELL_TO_OPEN`, `SELL_TO_CLOSE` |
| `close_contracts` | Optional JP-only close payload | Array of `{ "contract_id": "...", "quantity": ... }`, max 10 items |

JP stock order example:
```json
{
  "symbol": "AAPL",
  "side": "BUY",
  "order_type": "LIMIT",
  "limit_price": 180,
  "quantity": 10,
  "instrument_type": "EQUITY",
  "market": "US",
  "time_in_force": "DAY",
  "entrust_type": "QTY",
  "support_trading_session": "CORE",
  "combo_type": "NORMAL",
  "account_tax_type": "GENERAL"
}
```

---

## Security

- **Never share your AK/SK with AI models** — Do not paste your App Key or App Secret into chat prompts, AI assistants, or any LLM conversation. These credentials should only be configured via environment variables or `.env` files, never exposed in plain text to the model.
- **Credential isolation** — AK/SK are used only inside the SDK client process for initialization and request signing. They never appear in tool outputs, logs, or error messages.
- **Audit logging** — All order operations are logged with sanitized parameters (credentials stripped, prices masked) for compliance tracking.
- **Review before trading** — Always review order details proposed by the AI before confirming. Use `preview` actions before placing orders.
- **Default sandbox** — The skill defaults to UAT (sandbox) environment. You must explicitly set `WEBULL_ENVIRONMENT=prod` for live trading.
- **Risk controls** — Configurable notional limits, quantity limits, and symbol whitelist prevent accidental large orders.

---

## Troubleshooting

### `ModuleNotFoundError` or Wrong Python Version

If you see `ModuleNotFoundError: No module named 'webull_skill'` or `No module named 'dotenv'`, your `python3`/`python` command likely points to a different interpreter than the one `pip` installed into.

**Fix:** Use a virtual environment so everything stays in sync:

```bash
# macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Windows (Command Prompt):
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .

# Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

After this, use `webull-skill` (the installed console command) instead of `python3 webull_skill/cli.py`.

### 2FA Authentication Required

```bash
webull-skill auth
# Approve in Webull app, then re-run your command
```

### Device Not Registered

1. Open Webull mobile app → log in with your API account → complete device registration
2. Run `webull-skill auth`

### Market Data 401/403

Subscribe to quotes:
- US: [webullapp.com/quote](https://www.webullapp.com/quote) | [Guide](https://developer.webull.com/apis/docs/market-data-api/subscribe-quotes)
- HK: [webullapp.hk/quote](https://www.webullapp.hk/quote) | [Guide](https://developer.webull.hk/apis/docs/market-data-api/subscribe-quotes)
- JP: [webull.co.jp/pricing](https://www.webull.co.jp/pricing) | [Guide](https://developer.webull.co.jp/apis/docs/market-data-api/subscribe-quotes)

### Token Expired

```bash
rm -rf conf/token.txt        # macOS / Linux
del conf\token.txt            # Windows
webull-skill auth
```

---

## Project Structure

```
webull-openapi-skills/
├── pyproject.toml              # Package configuration
├── .env.example                # Configuration template
├── DISCLAIMER.md               # Risk disclaimer
├── LICENSE
├── README.md                   # This file
├── SKILL.md                    # Skill metadata for AI agents
├── webull_skill/               # Core Python package
│   ├── cli.py                  # CLI entry point
│   ├── config.py               # Configuration management
│   ├── sdk_client.py           # Webull SDK adapter
│   ├── audit.py                # Audit logging
│   ├── errors.py               # Error handling
│   ├── formatters.py           # Response formatting (region-aware)
│   ├── guards.py               # Order validation
│   ├── constants.py            # Enum constants
│   ├── region_config.py        # Region-specific settings
│   ├── risk_engine.py          # Risk limit checks
│   ├── env_router.py           # Endpoint routing
│   ├── result.py               # Structured JSON output
│   ├── runtime.py              # SDK logging control
│   ├── trading/                # Account, asset, instrument, order modules
│   └── market_data/            # Stock, futures, crypto, event modules
├── references/                 # API reference docs
├── tests/                      # Unit tests
└── conf/                       # Token storage (gitignored)
```

---

## Using with AI Coding Tools

This skill works as an MCP server. Below is how to integrate it with popular AI coding tools.

### Claude Code

Add to your MCP config (`~/.claude/claude_code_config.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "webull": {
      "command": "webull-skill",
      "args": ["mcp"],
      "env": {
        "WEBULL_APP_KEY": "your_app_key",
        "WEBULL_APP_SECRET": "your_app_secret",
        "WEBULL_REGION_ID": "us"
      }
    }
  }
}
```

### OpenAI Codex

Add to your project's `codex.json`:

```json
{
  "mcpServers": {
    "webull": {
      "command": "webull-skill",
      "args": ["mcp"],
      "env": {
        "WEBULL_APP_KEY": "your_app_key",
        "WEBULL_APP_SECRET": "your_app_secret",
        "WEBULL_REGION_ID": "us"
      }
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "webull": {
      "command": "webull-skill",
      "args": ["mcp"],
      "env": {
        "WEBULL_APP_KEY": "your_app_key",
        "WEBULL_APP_SECRET": "your_app_secret",
        "WEBULL_REGION_ID": "us"
      }
    }
  }
}
```

### Kiro

Kiro loads the skill automatically from `.kiro/skills/`. No extra configuration needed — just open this project in Kiro and start chatting.

### OpenClaw / Other MCP-Compatible Tools

Any tool that supports the MCP protocol can use this skill. Point it to:

```bash
webull-skill mcp
```

With environment variables `WEBULL_APP_KEY`, `WEBULL_APP_SECRET`, and `WEBULL_REGION_ID` set.

> **Note:** Run `pip install -e .` first to make the `webull-skill` command available. Ensure your `.env` is configured or pass credentials via the `env` block in your MCP config.

---

## Related Projects

- [webull-openapi-python-sdk](https://github.com/webull-inc/webull-openapi-python-sdk) — Official Python SDK
- [webull-mcp-server](https://github.com/webull-inc/webull-mcp-server) — MCP server for AI assistants

## Documentation

- US API: https://developer.webull.com/apis/docs
- HK API: https://developer.webull.hk/apis/docs
- US LLM-friendly: https://developer.webull.com/apis/llms.txt
- HK LLM-friendly: https://developer.webull.hk/apis/llms.txt

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
