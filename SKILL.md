---
name: webull-openapi
description: Trade stocks, options, futures, crypto, and event contracts on Webull. Query real-time and historical market data. Manage accounts and positions. Supports US, HK, and JP regions with configurable risk controls.
---

# Webull OpenAPI Skill

This skill lets you interact with Webull's trading platform through natural language. You can place orders, check market data, query account info, and manage positions — all via the official Webull Python SDK.

## What You Can Do

- **Trade**: Place, preview, modify, and cancel orders for stocks, options, futures, crypto, and event contracts
- **Market Data**: Get real-time snapshots, historical bars, tick data, quotes, and order flow for all asset classes
- **Accounts**: List accounts, check balances, view positions
- **Instruments**: Look up stock, crypto, futures, and event contract instruments; get company profile, analyst ratings, and target prices
- **Screener**: Top gainers/losers and most active stocks
- **Watchlist**: Create, manage, and query watchlists and their instruments

## Safety Rules

**All order-mutating operations require user confirmation before execution.**

Mutating actions: `place`, `replace`, `cancel`, `batch-place`, `algo-place`, `option-place`, `option-replace`, `option-strategy-place`, `futures-place`, `futures-replace`, `crypto-place`, `event-place`, `event-replace`.

Before executing any of these operations, the AI must:
1. Display a clear summary of the operation to the user, including:
   - Action type (place / replace / cancel)
   - Symbol, side, order type, quantity, price
   - Account being used
2. Explicitly ask the user to confirm (e.g., "Confirm this order? [Yes/No]")
3. Only proceed after receiving explicit user approval

Read-only operations (`account-list`, `balance`, `position`, `open`, `history`, `detail`, `instrument-*`, all `market-data` actions) do not require confirmation and can be executed immediately.

---

## Quick Examples

> **CLI command:** After `pip install -e .`, use `webull-skill` on all platforms (macOS, Linux, Windows). This console entry point is bound to the Python that ran `pip`, so it works regardless of what `python3` or `python` points to on your system.

> **Passing order JSON:** Prefer `--order-file <path>` (write JSON to a temp file first) over `--order-json '<inline>'`. Inline JSON with `--order-json` is fragile across shells — Windows bash, PowerShell, and some macOS terminals mangle quotes and escapes. Using `--order-file` avoids all shell quoting issues.

```bash
# Check your accounts
webull-skill trading --action account-list

# Get AAPL stock price
webull-skill market-data --action stock-snapshot --symbols AAPL

# Get account balance
webull-skill trading --action balance --account-id <id>

# Place a limit buy order (recommended: use --order-file)
# First write JSON to a file, then pass it:
#   echo '{"symbol":"AAPL","side":"BUY","order_type":"LIMIT","limit_price":180,"quantity":10,"instrument_type":"EQUITY","market":"US","time_in_force":"DAY","entrust_type":"QTY","support_trading_session":"CORE","combo_type":"NORMAL"}' > /tmp/order.json
#   webull-skill trading --action place --account-id <id> --order-file /tmp/order.json
#
# Alternative (inline, may fail on some shells):
webull-skill trading --action place --account-id <id> \
  --order-json '{"symbol":"AAPL","side":"BUY","order_type":"LIMIT","limit_price":180,"quantity":10,"instrument_type":"EQUITY","market":"US","time_in_force":"DAY","entrust_type":"QTY","support_trading_session":"CORE","combo_type":"NORMAL"}'

# Cancel an order
webull-skill trading --action cancel --account-id <id> --client-order-id <oid>
```

## CLI Entry Point

```
webull-skill [--env-file PATH] [--verbose-sdk-log] <module> --action <ACTION> [options]
```

Three modules: `trading`, `market-data`, `auth`.

---

## Module: trading

Instrument queries, account/asset operations, and all order operations.

### Instrument Queries

| Action | Description | Key Options |
|--------|-------------|-------------|
| `instrument-stock` | Stock/ETF instrument info | `--symbols AAPL,TSLA` |
| `instrument-crypto` | Crypto instrument info | `--symbols BTCUSD` |
| `instrument-futures-products` | Futures product codes | `--category US_FUTURES` |
| `instrument-futures-product-class` | Futures product classification groups | `--category US_FUTURES` |
| `instrument-futures-list` | Futures instruments by symbol | `--symbols ESM6` |
| `instrument-futures-by-code` | Futures by product code | `--code ES` |
| `instrument-event-series` | Event contract series | `--page-size 50` |
| `instrument-event-list` | Event instruments by series | `--series-symbol <sym>` |
| `instrument-event-categories` | Event contract categories | |
| `instrument-event-events` | Events within a series | `--series-symbol <sym>` |

### Instrument Fundamentals (US, HK, JP)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `instrument-company-profile` | Company profile (description, CEO, sector, etc.) | `--symbol AAPL` |
| `instrument-analyst-rating` | Analyst buy/hold/sell rating counts | `--symbol AAPL` |
| `instrument-analyst-target-price` | Analyst target price (mean/high/low/median) | `--symbol AAPL` |

```bash
# Get company profile
webull-skill trading --action instrument-company-profile --symbol AAPL

# Get analyst rating
webull-skill trading --action instrument-analyst-rating --symbol TSLA

# Get analyst target price
webull-skill trading --action instrument-analyst-target-price --symbol NVDA
```

### Account & Asset

| Action | Description | Key Options |
|--------|-------------|-------------|
| `account-list` | List all linked accounts | |
| `balance` | Account balance | `--account-id <id>` |
| `position` | Account positions | `--account-id <id>` |
| `position-detail` | Position details by instrument (JP only) | `--account-id <id> --instrument-id <id>` |

### Stock Orders

| Action | Description |
|--------|-------------|
| `place` | Place stock order (single, non-combo) |
| `preview` | Preview order without submitting |
| `replace` | Modify existing stock order |
| `batch-place` | Combo orders (OTO/OCO/OTOCO) — US only |
| `algo-place` | Algorithmic order (TWAP/VWAP/POV) — US only |

### Option Orders

| Action | Description |
|--------|-------------|
| `option-place` | Place single-leg option order |
| `option-preview` | Preview option order |
| `option-replace` | Modify option order |
| `option-strategy-place` | Multi-leg strategy (VERTICAL, STRADDLE, etc.) — US only |

### Futures / Crypto / Event Orders (US only)

| Action | Description |
|--------|-------------|
| `futures-place` | Place futures order |
| `futures-replace` | Modify futures order |
| `crypto-place` | Place crypto order (no replace supported) |
| `event-place` | Place event contract order |
| `event-replace` | Modify event contract order |

### Order Management

| Action | Description | Key Options |
|--------|-------------|-------------|
| `cancel` | Cancel an order | `--account-id`, `--client-order-id` |
| `open` | List open/pending orders | `--account-id` |
| `history` | Order history | `--account-id` |
| `detail` | Single order detail | `--account-id`, `--client-order-id` |
| `local-check` | Risk check only (no API call) | `--order-json` |

---

### Order JSON Format

Orders are passed via `--order-json` (inline string) or `--order-file` (path to a JSON file). **`--order-file` is strongly recommended** to avoid shell quoting issues.

> **Important:** The `place` and `replace` actions accept **different** JSON fields. Do NOT use `place` fields for `replace` — the CLI spreads JSON keys directly into the function, so unexpected fields cause errors.

> **`client_order_id` / `client_combo_order_id` rules:** Max 32 characters, must be alphanumeric only (letters and digits, no hyphens/underscores/special chars), and must be unique per account. If not provided, the system auto-generates one.

---

#### Place Order JSON (for `place`, `preview`)

> **Type note:** Stock place CLI does `float()` conversion internally, so strings technically work — but for consistency and to avoid issues, always use **number** types for numeric fields.

| Field | Required | JSON Type | Values / Description |
|-------|----------|-----------|----------------------|
| `combo_type` | Yes | string | `NORMAL` (single order). For combo: `MASTER`, `STOP_PROFIT`, `STOP_LOSS`, `OTO`, `OCO`, `OTOCO` |
| `symbol` | Yes | string | Ticker symbol, e.g. `AAPL`, `00700`, `BTCUSD`, `ESZ5` |
| `instrument_type` | Yes | string | `EQUITY`, `OPTION`, `FUTURES`, `CRYPTO`, `EVENT` |
| `market` | Yes | string | Region-dependent: US region `US`; HK region `US`, `HK`, `CN`; JP region `US`, `JP` |
| `side` | Yes | string | `BUY`, `SELL`, `SHORT` |
| `order_type` | Yes | string | See [Order Types by Market](#order-types-by-market) below |
| `time_in_force` | Yes | string | See [Time in Force](#time-in-force) below |
| `quantity` | Conditional | number (float) | Number of shares/contracts. Required when `entrust_type=QTY`. e.g. `10` — NOT `"10"` |
| `entrust_type` | Yes | string | `QTY` (by quantity) or `AMOUNT` (fractional shares / crypto by dollar amount) |
| `limit_price` | Conditional | number (float) | Required for `LIMIT`, `STOP_LOSS_LIMIT` orders, e.g. `180` — NOT `"180"` |
| `stop_price` | Conditional | number (float) | Required for `STOP_LOSS`, `STOP_LOSS_LIMIT` orders |
| `support_trading_session` | Region-dependent stock orders | string | Trading session. See [Trading Sessions](#trading-sessions) below |
| `total_cash_amount` | Conditional | number (float) | Required when `entrust_type=AMOUNT` (US fractional shares / crypto) |
| `trailing_type` | Conditional | string | Required for `TRAILING_STOP_LOSS`: `AMOUNT` or `PERCENTAGE` |
| `trailing_stop_step` | Conditional | number (float) | Required for `TRAILING_STOP_LOSS`: trail amount or percentage (0.01 = 1%) |
| `sender_sub_id` | No (HK broker) | string | Broker user UUID for third-party transactions (HK region, institutional only) |
| `no_party_ids` | No (HK broker) | array | BCAN party identifiers for HK stock orders (institutional only). See below |
| `account_tax_type` | JP stock orders | string | JP-only. Required for JP stock `place` / `preview`. Values: `GENERAL`, `SPECIFIC` |
| `margin_type` | JP margin account only | string | JP-only. `US_MARGIN` accounts only. Values: `ONE_DAY`, `INDEFINITE` |
| `position_intent` | JP margin account only | string | JP-only. `US_MARGIN` accounts only. Values: `BUY_TO_OPEN`, `BUY_TO_CLOSE`, `SELL_TO_OPEN`, `SELL_TO_CLOSE` |
| `close_contracts` | No (JP only) | array | JP-only close payload. Max 10 `{ "contract_id": "...", "quantity": ... }` items |

> **`quantity` vs `total_cash_amount`:** These two fields are mutually exclusive.
> - When `entrust_type=QTY`: provide `quantity` (number of shares/contracts)
> - When `entrust_type=AMOUNT`: provide `total_cash_amount` (dollar amount for fractional shares / crypto)
> - Do NOT provide both at the same time.

Stock limit buy example:
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
  "combo_type": "NORMAL"
}
```

HK stock order example (with BCAN, institutional/broker only):
```json
{
  "symbol": "00700",
  "side": "BUY",
  "order_type": "ENHANCED_LIMIT",
  "limit_price": 350,
  "quantity": 100,
  "instrument_type": "EQUITY",
  "market": "HK",
  "time_in_force": "DAY",
  "entrust_type": "QTY",
  "combo_type": "NORMAL",
  "sender_sub_id": "<broker_user_uuid>",
  "no_party_ids": [
    {
      "party_id": "ABC123.2568",
      "party_id_source": "D",
      "party_role": "3"
    }
  ]
}
```

`no_party_ids` array item fields:

| Field | Required | Description |
|-------|----------|-------------|
| `party_id` | Yes | BCAN ID, format: `CE_NUMBER.BCAN` e.g. `ABC123.2568` |
| `party_id_source` | Yes | Always `"D"` (Proprietary/Custom Code) |
| `party_role` | Yes | Always `"3"` (Client ID / BCAN Field) |

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

JP margin-account example:
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
  "account_tax_type": "GENERAL",
  "margin_type": "ONE_DAY",
  "position_intent": "BUY_TO_OPEN"
}
```

---

#### Option Place JSON (for `option-place`, `option-preview`)

> **⚠️ Type-sensitive:** Option place uses `**o` spread — JSON types must match function signatures exactly. `quantity` must be **integer**, `strike_price`/`limit_price`/`stop_price` must be **number** (float), not strings.

| Field | Required | JSON Type | Values / Description |
|-------|----------|-----------|----------------------|
| `symbol` | Yes | string | Underlying symbol, e.g. `AAPL` |
| `instrument_type` | Yes | string | `OPTION` |
| `option_type` | Yes | string | `CALL` or `PUT` |
| `strike_price` | Yes | number (float) | Strike price, e.g. `220.00` — NOT `"220.00"` |
| `expiration_date` | Yes | string | Expiration date, format `yyyy-MM-dd`, e.g. `"2026-06-19"` |
| `side` | Yes | string | `BUY`, `SELL`, `SHORT` |
| `order_type` | Yes | string | `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT` |
| `time_in_force` | Yes | string | `DAY`, `GTC`. Sell-side only supports `DAY` |
| `quantity` | Yes | number (int) | Number of contracts, e.g. `1` — NOT `"1"` |
| `limit_price` | Conditional | number (float) | Required for `LIMIT` orders, e.g. `11.25` — NOT `"11.25"` |
| `stop_price` | Conditional | number (float) | Required for `STOP_LOSS` orders |
| `position_intent` | No | string | Position strategy (US only). `BUY_TO_OPEN`, `BUY_TO_CLOSE`, `SELL_TO_OPEN`, `SELL_TO_CLOSE`. Must match `side` |
| `sender_sub_id` | No (HK broker) | string | Broker user UUID (HK region, institutional only). No BCAN needed for options |

Option single-leg example:
```json
{
  "symbol": "AAPL",
  "instrument_type": "OPTION",
  "option_type": "CALL",
  "strike_price": 220.00,
  "expiration_date": "2026-06-19",
  "side": "BUY",
  "order_type": "LIMIT",
  "limit_price": 11.25,
  "quantity": 1,
  "time_in_force": "DAY",
  "position_intent": "BUY_TO_OPEN"
}
```

---

#### Option Strategy Place JSON (for `option-strategy-place`)

> **⚠️ Type-sensitive:** Same as option-place — numeric fields must be numbers, not strings.

| Field | Required | JSON Type | Values / Description |
|-------|----------|-----------|----------------------|
| `strategy` | Yes | string | `VERTICAL`, `STRADDLE`, `STRANGLE`, `BUTTERFLY`, `CONDOR`, `CALENDAR`, `DIAGONAL`, `IRON_BUTTERFLY`, `IRON_CONDOR`, `COLLAR_WITH_STOCK`, `COVERED_STOCK` |
| `symbol` | Yes | string | Underlying symbol |
| `order_type` | Yes | string | `LIMIT`, `MARKET` |
| `time_in_force` | Yes | string | `DAY`, `GTC` |
| `quantity` | No | number (int) | Number of contracts per leg |
| `limit_price` | Conditional | number (float) | Net debit/credit price for the strategy |
| `legs` | Yes | array | Array of leg objects (see below) |

Each leg object:

| Field | Required | JSON Type | Values |
|-------|----------|-----------|--------|
| `side` | Yes | string | `BUY`, `SELL` |
| `quantity` | Yes | string | Contracts for this leg |
| `symbol` | Yes | string | Underlying symbol |
| `strike_price` | Yes | string | Strike price |
| `option_expire_date` | Yes | string | `yyyy-MM-dd` |
| `instrument_type` | Yes | string | `OPTION` |
| `option_type` | Yes | string | `CALL` or `PUT` |
| `market` | Yes | string | `US` |

---

#### Futures Place JSON (for `futures-place`)

> **⚠️ Type-sensitive:** Futures place uses `**o` spread — `quantity`/`limit_price`/`stop_price` must be **number** (float), not strings.

| Field | Required | JSON Type | Values / Description |
|-------|----------|-----------|----------------------|
| `symbol` | Yes | string | Futures symbol, e.g. `ESZ5`, `NQM6` |
| `side` | Yes | string | `BUY`, `SELL` |
| `order_type` | Yes | string | `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TRAILING_STOP_LOSS` |
| `time_in_force` | Yes | string | `DAY`, `GTC` |
| `quantity` | Yes | number (float) | Number of contracts, e.g. `1` — NOT `"1"` |
| `limit_price` | Conditional | number (float) | Required for `LIMIT`, `STOP_LOSS_LIMIT` |
| `stop_price` | Conditional | number (float) | Required for `STOP_LOSS`, `STOP_LOSS_LIMIT` |

Futures example:
```json
{
  "symbol": "ESZ5",
  "side": "BUY",
  "order_type": "LIMIT",
  "limit_price": 4500,
  "quantity": 1,
  "time_in_force": "DAY"
}
```

---

#### Crypto Place JSON (for `crypto-place`)

> **⚠️ Type-sensitive:** Crypto place uses `**o` spread — `quantity`/`limit_price`/`stop_price`/`total_cash_amount` must be **number** (float), not strings.

| Field | Required | JSON Type | Values / Description |
|-------|----------|-----------|----------------------|
| `symbol` | Yes | string | e.g. `BTCUSD`, `ETHUSD` |
| `side` | Yes | string | `BUY`, `SELL` |
| `order_type` | Yes | string | `MARKET` (tif **must** be `IOC`), `LIMIT` (tif `DAY`/`GTC`), `STOP_LOSS_LIMIT` (tif `DAY`/`GTC`) |
| `time_in_force` | Yes | string | `IOC` (only for `MARKET`), `DAY` or `GTC` (for `LIMIT`/`STOP_LOSS_LIMIT`) |
| `entrust_type` | Yes | string | `QTY` or `AMOUNT` |
| `quantity` | Conditional | number (float) | Required when `entrust_type=QTY`. Supports up to 8 decimal places |
| `total_cash_amount` | Conditional | number (float) | Required when `entrust_type=AMOUNT` |
| `limit_price` | Conditional | number (float) | Required for `LIMIT`, `STOP_LOSS_LIMIT` |
| `stop_price` | Conditional | number (float) | Required for `STOP_LOSS_LIMIT` |

> Note: Crypto does NOT support replace (modify) orders. When selling, position must not fall below $2.

Crypto example:
```json
{
  "symbol": "BTCUSD",
  "side": "BUY",
  "order_type": "LIMIT",
  "limit_price": 80000,
  "quantity": 0.003,
  "time_in_force": "DAY",
  "entrust_type": "QTY"
}
```

---

#### Event Contract Place JSON (for `event-place`)

> **⚠️ Type-sensitive:** Event place uses `**o` spread — `quantity` and `limit_price` must be **number** (float), not strings.

| Field | Required | JSON Type | Values / Description |
|-------|----------|-----------|----------------------|
| `symbol` | Yes | string | Event contract symbol |
| `side` | Yes | string | `BUY`, `SELL` |
| `quantity` | Yes | number (float) | Number of contracts. Accepts 0-2 decimal places |
| `limit_price` | Yes | number (float) | Limit price (LIMIT orders only) |
| `event_outcome` | Yes | string | `yes` or `no` |
| `order_type` | No | string | Default `LIMIT` (only LIMIT supported) |
| `time_in_force` | No | string | Default `DAY` (only DAY supported) |

Event contract example:
```json
{
  "symbol": "KXRATECUTCOUNT-26DEC31-T3",
  "side": "BUY",
  "quantity": 5,
  "limit_price": 0.10,
  "event_outcome": "yes"
}
```

---

#### Algo Place JSON (for `algo-place`) — US only

> **⚠️ Type-sensitive:** Algo place uses `**o` spread — `quantity`/`limit_price` must be **number**, `target_vol_percent`/`max_target_percent` must be **integer**.

| Field | Required | JSON Type | Values / Description |
|-------|----------|-----------|----------------------|
| `symbol` | Yes | string | Stock symbol |
| `side` | Yes | string | `BUY`, `SELL` |
| `quantity` | Yes | number (float) | Number of shares |
| `algo_type` | Yes | string | `TWAP`, `VWAP`, `POV` |
| `order_type` | No | string | `MARKET` or `LIMIT` (default `LIMIT`) |
| `limit_price` | Conditional | number (float) | Required for `LIMIT` order type |
| `max_target_percent` | Conditional | number (int) | Required for `TWAP`/`VWAP`. Integer 1-20 |
| `target_vol_percent` | Conditional | number (int) | Required for `POV`. Integer 1-20 |
| `algo_start_time` | No | string | US Eastern Time, `HH:mm:ss` format, e.g. `"09:30:00"` |
| `algo_end_time` | No | string | US Eastern Time, `HH:mm:ss` format, e.g. `"16:00:00"` |

Algo TWAP example:
```json
{
  "symbol": "AAPL",
  "side": "BUY",
  "quantity": 100,
  "algo_type": "TWAP",
  "order_type": "LIMIT",
  "limit_price": 180,
  "max_target_percent": 10,
  "algo_start_time": "09:30:00",
  "algo_end_time": "16:00:00"
}
```

---

### Replace (Modify) Order JSON

Replace actions use a **different, smaller** set of fields. Only include `client_order_id` plus the fields you want to change.

> **CRITICAL:** Do NOT include `symbol`, `side`, `instrument_type`, `market`, `entrust_type`, or `combo_type` in replace JSON — these cause `unexpected keyword argument` errors.

> **Note:** `client_order_id` MUST be in the JSON body. The `--client-order-id` CLI flag is NOT passed to replace functions.

#### Stock Replace (`replace`)

| Field | Required | JSON Type | Description |
|-------|----------|-----------|-------------|
| `client_order_id` | Yes | string | The order to modify |
| `quantity` | No | number (float) | New quantity |
| `limit_price` | No | number (float) | New limit price |
| `stop_price` | No | number (float) | New stop price |
| `time_in_force` | No | string | `DAY`, `GTC` |
| `order_type` | No | string | New order type |
| `trailing_type` | No | string | `AMOUNT` or `PERCENTAGE` |
| `trailing_stop_step` | No | number (float) | New trailing stop spread |
| `target_vol_percent` | No | number (int) | For algo orders (1-20) |
| `max_target_percent` | No | number (int) | For algo orders (1-20) |
| `algo_start_time` | No | string | For algo orders, `HH:mm:ss` |
| `algo_end_time` | No | string | For algo orders, `HH:mm:ss` |
| `close_contracts` | JP conditional | array | JP-only close payload. Required on replace if the original order used `close_contracts` |

JP `close_contracts` replace rules:

- If the original JP stock order contains `close_contracts`, every replace request for that order must include `close_contracts`.
- The `close_contracts` structure must remain the same as the original order.
- The `close_contracts` array length must remain the same as the original order.
- Each item's `contract_id` must remain exactly the same as the original order.
- If `close_contracts` is modified, only each item's internal `quantity` may be changed.
- `close_contracts` can contain at most 10 contracts.
- If `contract_id` is not passed on an original close order, backend closes by first-in-first-out. If a contract-level close order did pass `contract_id`, preserve it during replace.

`close_contracts` item fields:

| Field | Required | JSON Type | Description |
|-------|----------|-----------|-------------|
| `contract_id` | Yes | string | Contract ID from the original order |
| `quantity` | Yes | string | Quantity to close under this contract ID, e.g. `"10"` |

Stock replace example — change quantity from 1 to 2:
```json
{
  "client_order_id": "7af9c5c03a6f4e6ca46a194609f158e1",
  "quantity": 2,
  "limit_price": 258
}
```

JP stock replace example with `close_contracts` — keep the same contract structure and change only internal `quantity`:
```json
{
  "client_order_id": "7af9c5c03a6f4e6ca46a194609f158e1",
  "quantity": 2,
  "close_contracts": [
    {
      "contract_id": "contract-1",
      "quantity": "2"
    }
  ]
}
```

Replace example using `--order-file` (recommended):
```bash
echo '{"client_order_id":"<oid>","quantity":2}' > /tmp/replace.json
webull-skill trading --action replace --account-id <id> --order-file /tmp/replace.json
```

#### Option Replace (`option-replace`)

> **⚠️ Type-sensitive:** Option replace requires `quantity` as **integer** (not string) and `limit_price`/`stop_price` as **number** (not string). Passing `"2"` instead of `2` will cause errors.

| Field | Required | JSON Type | Description |
|-------|----------|-----------|-------------|
| `client_order_id` | Yes | string | The order to modify |
| `quantity` | No | number (int) | New quantity — must be integer, NOT string |
| `limit_price` | No | number (float) | New limit price — must be number, NOT string |
| `stop_price` | No | number (float) | New stop price — must be number, NOT string |
| `time_in_force` | No | string | `DAY`, `GTC` |

Option replace example:
```json
{
  "client_order_id": "abc123def456",
  "quantity": 2,
  "limit_price": 3.5
}
```

> Note: Option leg IDs are auto-fetched from order detail. No need to provide `legs` manually.

#### Futures Replace (`futures-replace`)

Futures modification rules (from official API docs):
- Market orders: only `quantity` can be modified
- Limit orders: `order_type` (can only change to `MARKET`), `time_in_force`, `quantity`, `limit_price`
- Stop orders: `order_type` (can only change to `MARKET`), `time_in_force`, `quantity`, `stop_price`
- Stop limit orders: `order_type` (can only change to `LIMIT`), `time_in_force`, `quantity`, `limit_price`, `stop_price`
- Trailing stop orders: only `trailing_stop_step` can be modified

| Field | Required | JSON Type | Description |
|-------|----------|-----------|-------------|
| `client_order_id` | Yes | string | The order to modify |
| `quantity` | No | number (float) | New quantity |
| `limit_price` | No | number (float) | New limit price |
| `order_type` | No | string | New order type (restricted, see rules above) |

Futures replace example:
```json
{
  "client_order_id": "abc123def456",
  "quantity": 2,
  "limit_price": 4550
}
```

#### Event Replace (`event-replace`)

| Field | Required | JSON Type | Description |
|-------|----------|-----------|-------------|
| `client_order_id` | Yes | string | The order to modify |
| `quantity` | No | number (float) | New quantity |
| `limit_price` | No | number (float) | New limit price |

Event replace example:
```json
{
  "client_order_id": "abc123def456",
  "quantity": 10,
  "limit_price": 0.15
}
```

#### Crypto Replace

**Not supported.** Cancel and re-place instead.

---

### Order Types by Market

| Market | Supported Order Types |
|--------|----------------------|
| US stocks/ETFs | `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TRAILING_STOP_LOSS` |
| US stocks (institutional) | Also: `MARKET_ON_OPEN`, `MARKET_ON_CLOSE`, `LIMIT_ON_OPEN` |
| US options | `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT` |
| US futures | `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TRAILING_STOP_LOSS` |
| US crypto | `MARKET`, `LIMIT`, `STOP_LOSS_LIMIT` |
| US event contracts | `LIMIT` only |
| HK stocks | `ENHANCED_LIMIT`, `AT_AUCTION`, `AT_AUCTION_LIMIT` |
| CN A-shares (via HK) | `LIMIT` only |

### Time in Force

| Value | Description | Supported By |
|-------|-------------|--------------|
| `DAY` | Valid for current trading day only | All instruments |
| `GTC` | Good-Till-Canceled (up to 60 days) | US stocks, options, futures, crypto |
| `IOC` | Immediate-Or-Cancel (unfilled portion canceled) | Crypto `MARKET` orders only |

### Trading Sessions

Natural language "trading session" maps to the order JSON field `support_trading_session`.

| Value | Description | Supported Regions |
|-------|-------------|-------------------|
| `CORE` | Regular hours (9:30 AM - 4:00 PM ET) | US, HK, JP |
| `ALL` | Extended hours (pre-market + after-hours) | US, HK, JP |
| `NIGHT` | Night session only | US, HK, JP |
| `ALL_DAY` | Included overnight hours, 8:00 p.m. ET - 8:00 p.m. ET the next day | HK, JP |

### Combo Types (US stocks only)

| Value | Description |
|-------|-------------|
| `NORMAL` | Standard single order |
| `MASTER` | Simple order + take profit or stop loss |
| `STOP_PROFIT` | Take profit order (child of MASTER) |
| `STOP_LOSS` | Stop loss order (child of MASTER) |
| `OTO` | One Triggers Other |
| `OCO` | One Cancels Other |
| `OTOCO` | One Triggers a One Cancels Other |

### Option Strategies (US only)

`SINGLE`, `COVERED_STOCK`, `VERTICAL`, `STRADDLE`, `STRANGLE`, `CALENDAR`, `DIAGONAL`, `BUTTERFLY`, `CONDOR`, `COLLAR_WITH_STOCK`, `IRON_BUTTERFLY`, `IRON_CONDOR`

### Algo Types (US only)

| Type | Description | Required Param |
|------|-------------|----------------|
| `TWAP` | Time Weighted Average Price | `max_target_percent` (1-20) |
| `VWAP` | Volume Weighted Average Price | `max_target_percent` (1-20) |
| `POV` | Percentage of Volume | `target_vol_percent` (1-20) |

---

## Module: market-data

Real-time and historical market data for all asset classes.

### Stock

| Action | Description | Key Options |
|--------|-------------|-------------|
| `stock-snapshot` | Real-time snapshot | `--symbols AAPL,TSLA` |
| `stock-bars` | OHLCV bars (single symbol) | `--symbol AAPL --timespan D --count 200` |
| `stock-batch-bars` | OHLCV bars (multiple symbols) | `--symbols AAPL,TSLA --timespan D` |
| `stock-tick` | Tick-by-tick trades | `--symbol AAPL --count 30` |
| `stock-quotes` | Bid/ask depth | `--symbol AAPL --depth 5` |
| `stock-footprint` | Large order flow | `--symbols AAPL --timespan M1` |
| `stock-noii-bars` | NOII K-line data (auction imbalance) | `--symbol AAPL --imbalance-action-type PRE_OPEN` |
| `stock-noii-snapshot` | NOII real-time snapshot | `--symbol AAPL --imbalance-action-type PRE_CLOSE` |

#### `stock-bars` / `stock-batch-bars` — Time Range Support

Both bar actions support optional time range filtering via `--start-time` and `--end-time` (Unix timestamp in **milliseconds**, long integer):

```bash
# Single symbol bars with time range
webull-skill market-data --action stock-bars --symbol AAPL --timespan D \
  --start-time 1700000000000 --end-time 1710000000000

# Batch bars with time range
webull-skill market-data --action stock-batch-bars --symbols AAPL,TSLA --timespan H1 \
  --start-time 1700000000000 --end-time 1710000000000
```

#### NOII (Net Order Imbalance Indicator)

NOII data is published by NASDAQ before opening and closing auctions, providing a preview of market supply and demand.

- `--imbalance-action-type`: `PRE_OPEN` (opening auction) or `PRE_CLOSE` (closing auction)
- `stock-noii-snapshot` is only live during auction windows (9:28–9:30 AM ET and 3:50–4:00 PM ET); outside these windows, historical data is returned

```bash
# NOII K-line for opening auction
webull-skill market-data --action stock-noii-bars --symbol AAPL --imbalance-action-type PRE_OPEN

# NOII snapshot for closing auction
webull-skill market-data --action stock-noii-snapshot --symbol AAPL --imbalance-action-type PRE_CLOSE
```

### Futures (US only)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `futures-snapshot` | Futures snapshot | `--symbols ESM6` |
| `futures-bars` | Futures OHLCV | `--symbols ESM6 --timespan D` |
| `futures-tick` | Futures ticks | `--symbol ESM6 --count 30` |
| `futures-depth` | Order book depth | `--symbol ESM6 --depth 5` |
| `futures-footprint` | Futures order flow | `--symbols ESM6 --timespan M1` |

### Crypto (US only)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `crypto-snapshot` | Crypto snapshot | `--symbols BTCUSD` |
| `crypto-bars` | Crypto OHLCV | `--symbols BTCUSD --timespan D` |

### Event Contracts (US only)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `event-snapshot` | Event snapshot | `--symbols <sym>` |
| `event-depth` | Event depth | `--symbol <sym> --depth 5` |
| `event-bars` | Event OHLCV | `--symbols <sym> --timespan D` |
| `event-tick` | Event ticks | `--symbol <sym> --count 30` |

### Screener (US, HK, JP)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `stock-gainers-losers` | Top gainers or losers by price change | `--rank-type DAY_1 --direction DESC` |
| `stock-most-active` | Most actively traded stocks | `--rank-type VOLUME` |

#### `stock-gainers-losers` Options

| Option | Required | Description |
|--------|----------|-------------|
| `--rank-type` | Yes | Time period: `PRE_MARKET`, `AFTER_MARKET`, `MIN_3`, `MIN_5`, `DAY_1`, `DAY_5`, `MONTH_1`, `MONTH_3`, `WEEK_52` |
| `--category` | No | Default `US_STOCK` |
| `--sort-by` | No | Secondary sort: `CHANGE_RATIO`, `VOLUME`, `MARKET_VALUE`, `TURNOVER`, `AMPLITUDE`, etc. Default `CHANGE_RATIO` |
| `--direction` | No | `DESC` for gainers, `ASC` for losers |
| `--page-index` | No | Page number starting from 1 |
| `--page-size` | No | Records per page |

#### `stock-most-active` Options

| Option | Required | Description |
|--------|----------|-------------|
| `--category` | No | Default `US_STOCK` |
| `--rank-type` | No | `VOLUME`, `RELATIVE_VOLUME_10D`, `TURNOVER`, `TURNOVER_RATE`, `AMPLITUDE`. Default `VOLUME` |
| `--sort-by` | No | Secondary sort field |
| `--direction` | No | `ASC` or `DESC`. Default `DESC` |
| `--page-index` | No | Page number starting from 1 |
| `--page-size` | No | Records per page |

```bash
# Top 20 gainers today
webull-skill market-data --action stock-gainers-losers \
  --rank-type DAY_1 --direction DESC --page-size 20

# Top losers today
webull-skill market-data --action stock-gainers-losers \
  --rank-type DAY_1 --direction ASC --page-size 20

# Most active by volume
webull-skill market-data --action stock-most-active --rank-type VOLUME

# Most active by relative volume (10-day)
webull-skill market-data --action stock-most-active --rank-type RELATIVE_VOLUME_10D
```

### Watchlist (US, HK, JP)

Watchlist operations manage saved lists of instruments. Maximum 20 watchlists, 1000 instruments total across all watchlists. Does not support futures, options, or event contracts.

- US region: supports US stocks and HK stocks
- HK region: supports HK stocks and US stocks
- JP region: supports US stocks

| Action | Description | Key Options |
|--------|-------------|-------------|
| `watchlist-list` | Get all watchlists | |
| `watchlist-create` | Create a new watchlist | `--watchlist-name <name>` |
| `watchlist-delete` | Delete a watchlist | `--watchlist-id <id>` |
| `watchlist-update` | Update watchlist name or sort | `--watchlist-id <id> --watchlist-name <name>` |
| `watchlist-instruments-list` | Get instruments in a watchlist | `--watchlist-id <id>` |
| `watchlist-instruments-add` | Add instruments to a watchlist | `--watchlist-id <id> --instruments-json '[...]'` |
| `watchlist-instruments-remove` | Remove instruments from a watchlist | `--watchlist-id <id> --instruments-json '[...]'` |
| `watchlist-instruments-update` | Update instrument sort order | `--watchlist-id <id> --instruments-json '[...]'` |

#### `--instruments-json` Format

Pass a JSON array of instrument objects. Fields vary by operation:

| Operation | Required Fields | Optional Fields |
|-----------|----------------|-----------------|
| `add` | `symbol`, `category` | `sort` |
| `remove` | `symbol`, `category` | |
| `update` | `symbol`, `category`, `sort` | |

```bash
# List all watchlists
webull-skill market-data --action watchlist-list

# Create a watchlist
webull-skill market-data --action watchlist-create --watchlist-name "My Tech Stocks"

# Add instruments (use --instruments-json)
webull-skill market-data --action watchlist-instruments-add \
  --watchlist-id <id> \
  --instruments-json '[{"symbol":"AAPL","category":"US_STOCK","sort":1},{"symbol":"TSLA","category":"US_STOCK","sort":2}]'

# Remove instruments
webull-skill market-data --action watchlist-instruments-remove \
  --watchlist-id <id> \
  --instruments-json '[{"symbol":"AAPL","category":"US_STOCK"}]'

# Delete a watchlist
webull-skill market-data --action watchlist-delete --watchlist-id <id>
```

### Common Options

| Option | Default | Description |
|--------|---------|-------------|
| `--category` | auto | See [Category Values](#category-values) below |
| `--timespan` | `D` | `M1`, `M5`, `M15`, `M30`, `H1`, `H4`, `D`, `W` |
| `--count` | `200` | Number of bars/ticks |
| `--depth` | `1` | Order book depth levels |
| `--extend-hour-required` | false | Include extended hours |
| `--overnight-required` | false | Include overnight data |
| `--start-time` | (none) | Start timestamp in milliseconds (Long), for bar actions |
| `--end-time` | (none) | End timestamp in milliseconds (Long), for bar actions |
| `--imbalance-action-type` | `PRE_OPEN` | NOII type: `PRE_OPEN` or `PRE_CLOSE` |

### Category Values

Category determines which market's data you're querying. It varies by region:

**US Region (`WEBULL_REGION_ID=us`):**

| Category | Description |
|----------|-------------|
| `US_STOCK` | US stocks (default for stock actions) |
| `US_ETF` | US ETFs |
| `US_FUTURES` | US futures (default for futures actions) |
| `US_CRYPTO` | US crypto (default for crypto actions) |
| `US_EVENT` | US event contracts (default for event actions) |

**HK Region (`WEBULL_REGION_ID=hk`):**

| Category | Description |
|----------|-------------|
| `US_STOCK` | US stocks (traded via HK account) |
| `US_ETF` | US ETFs (traded via HK account) |
| `HK_STOCK` | Hong Kong stocks |
| `CN_STOCK` | China Connect A-shares |

**JP Region (`WEBULL_REGION_ID=jp`):**

| Category | Description |
|----------|-------------|
| `US_STOCK` | US stocks (traded via JP account) |
| `US_ETF` | US ETFs (traded via JP account) |

Examples:
```bash
# US stock (default for US region)
webull-skill market-data --action stock-snapshot --symbols AAPL

# HK stock (must specify category for HK region)
webull-skill market-data --action stock-snapshot --symbols 00700 --category HK_STOCK

# China Connect A-share
webull-skill market-data --action stock-snapshot --symbols 600519 --category CN_STOCK

# JP region US stock
WEBULL_REGION_ID=jp webull-skill market-data --action stock-snapshot --symbols AAPL --category US_STOCK
```

---

## Module: auth

```bash
webull-skill auth
```

Interactive 2FA authentication. Run once before first use. The SDK waits up to 5 minutes for you to approve in the Webull mobile app. Token is cached and auto-refreshes.

---

## Output Format

All operations output formatted text directly to stdout, with a region-aware disclaimer at the top:

```
⚠️ Disclaimer: The information provided by this tool is for reference only ...

=== Stock Snapshot: AAPL ===
  Symbol:          AAPL
  Price:           255.92
  Pre Close:       255.63
  Change:          0.29
  ...
```

- Success: disclaimer + formatted data to stdout, exit code 0
- Error: error message to stderr, exit code 1
- US/JP region: English disclaimer only
- HK region: English + Simplified Chinese + Traditional Chinese disclaimer

---

## Configuration

Via `.env` file or environment variables. Required:

```
WEBULL_APP_KEY=<your_app_key>
WEBULL_APP_SECRET=<your_app_secret>
```

Region selection:

```env
# Choose one region:
WEBULL_REGION_ID=us
# WEBULL_REGION_ID=hk
# WEBULL_REGION_ID=jp

# Sandbox by default; set prod only for live trading.
WEBULL_ENVIRONMENT=uat
```

**`.env` lookup order** (when `--env-file` is not specified):
1. `$WEBULL_CONFIG_DIR/.env` — if `WEBULL_CONFIG_DIR` is set
2. `<project_root>/.env` — default (sibling of `webull_skill/`)
3. Current working directory `.env` — last resort

> To keep credentials outside the project directory, set `WEBULL_CONFIG_DIR` as a **system environment variable** (e.g. in `~/.zshrc`), then place your `.env` at `$WEBULL_CONFIG_DIR/.env`. Setting `WEBULL_CONFIG_DIR` inside a `.env` file has no effect — it must be set before the process starts.

Optional:

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBULL_ENVIRONMENT` | `uat` | `uat` (sandbox) or `prod` (live) |
| `WEBULL_REGION_ID` | `us` | `us`, `hk`, or `jp` |
| `WEBULL_MAX_ORDER_NOTIONAL_USD` | `10000` | Max order value (USD) |
| `WEBULL_MAX_ORDER_NOTIONAL_HKD` | `80000` | Max order value for HK market (HKD) |
| `WEBULL_MAX_ORDER_NOTIONAL_CNH` | `70000` | Max order value for CN market (CNH) |
| `WEBULL_MAX_ORDER_NOTIONAL_JPY` | `1500000` | Max order value for JP market (JPY) |
| `WEBULL_MAX_ORDER_QUANTITY` | `1000` | Max shares per order |
| `WEBULL_SYMBOL_WHITELIST` | (none) | Comma-separated allowed symbols |
| `WEBULL_CONFIG_DIR` | (none) | **System env var only** (not in `.env`). Moves `.env` lookup and token storage to this directory |
| `WEBULL_TOKEN_DIR` | `<project_root>/conf/` | Token storage directory |
| `WEBULL_AUDIT_LOG_FILE` | (stderr) | Audit log file path |
| `WEBULL_LOG_LEVEL` | `WARNING` | SDK log level |

---

## Region Support

| Feature | US | HK | JP |
|---------|:--:|:--:|:--:|
| Stock trading | ✓ | ✓ (US/HK/CN) | ✓ (US/JP) |
| Options | ✓ | ✓ (US only) | ✗ |
| Futures | ✓ | ✗ | ✗ |
| Crypto | ✓ | ✗ | ✗ |
| Event contracts | ✓ | ✗ | ✗ |
| Combo orders | ✓ | ✗ | ✗ |
| Algo orders | ✓ | ✗ | ✗ |
| Trailing stop loss | ✓ | ✗ | ✗ |
| Fractional shares | ✓ (US market) | ✗ | ✗ |
| Company profile | ✓ | ✓ | ✓ |
| Analyst rating / target price | ✓ | ✓ | ✓ |
| NOII bars / snapshot | ✓ | ✓ | ✓ |
| Screener (gainers/losers/active) | ✓ | ✓ | ✓ |
| Watchlist | ✓ | ✓ | ✓ |

### HK-Specific Notes

- HK stocks use order types: `ENHANCED_LIMIT`, `AT_AUCTION`, `AT_AUCTION_LIMIT`
- CN A-shares (Stock Connect): `LIMIT` only, disabled by default — contact Webull to enable
- Board lot sizes vary by HK stock
- No combo orders, algo orders, futures, crypto, or event contracts in HK region
- HK stock orders (institutional/broker): require `sender_sub_id` and `no_party_ids` (BCAN)
- HK US options (institutional/broker): support `sender_sub_id` only, no BCAN needed

### JP-Specific Notes

- Configure JP with `WEBULL_REGION_ID=jp`; sandbox uses `WEBULL_ENVIRONMENT=uat`.
- JP supports stock/ETF market data and stock order management. Futures, crypto, event contracts, options, combo orders, and algo orders are not supported in JP.
- JP stock instrument categories are `US_STOCK` and `US_ETF`.
- JP stock order markets are `US` and `JP`.
- JP market orders support `LIMIT` and `MARKET`; JP market time in force is `DAY`.
- US market orders in JP support `LIMIT`, `MARKET`, `STOP_LOSS`, `STOP_LOSS_LIMIT` with `DAY` or `GTC`.
- JP stock accounts are identified by `account_type`: `CASH` or `US_MARGIN`.
- `account_tax_type` is required for JP stock `place` and `preview`; valid values are `GENERAL` and `SPECIFIC`.
- `margin_type` and `position_intent` are valid only for JP `US_MARGIN` accounts.
- `close_contracts` is JP-only and accepts up to 10 objects with `contract_id` and positive `quantity`.

---

## Rate Limits

### US Region
- Market data: 600 req/min
- Order place/replace/cancel: 600 req/min
- Order query: 2 req/2s
- Auth: 10 req/30s

### HK Region
- Market data: 60 req/60s
- Order place: 15 req/s (US stocks), 1 req/s (HK/A-share)
- Order preview: 40 req/10s
- Order query: 40 req/2s

### JP Region
- Instrument lookup: 60 req/min per AppId
- Other endpoint limits follow the JP developer portal for the enabled account/API plan

---

## Official API Documentation

- US: https://developer.webull.com/apis/docs/webull-open-api-reference
- HK: https://developer.webull.hk/apis/docs/webull-open-api-reference
- JP: https://developer.webull.co.jp/apis/docs/webull-open-api-reference

---

## Disclaimer

The information provided by this tool is for reference only and does not constitute investment advice. Trading involves risk; please make decisions carefully.
