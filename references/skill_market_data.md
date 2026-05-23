# Module: market-data

Real-time and historical market data for all asset classes.

## Stock

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

### `stock-bars` / `stock-batch-bars` — Time Range Support

Both bar actions support optional time range filtering via `--start-time` and `--end-time` (Unix timestamp in **milliseconds**, long integer):

```bash
# Single symbol bars with time range
webull-skill market-data --action stock-bars --symbol AAPL --timespan D \
  --start-time 1700000000000 --end-time 1710000000000

# Batch bars with time range
webull-skill market-data --action stock-batch-bars --symbols AAPL,TSLA --timespan H1 \
  --start-time 1700000000000 --end-time 1710000000000
```

### NOII (Net Order Imbalance Indicator)

NOII data is published by NASDAQ before opening and closing auctions, providing a preview of market supply and demand.

- `--imbalance-action-type`: `PRE_OPEN` (opening auction) or `PRE_CLOSE` (closing auction)
- `stock-noii-snapshot` is only live during auction windows (9:28–9:30 AM ET and 3:50–4:00 PM ET); outside these windows, historical data is returned

```bash
# NOII K-line for opening auction
webull-skill market-data --action stock-noii-bars --symbol AAPL --imbalance-action-type PRE_OPEN

# NOII snapshot for closing auction
webull-skill market-data --action stock-noii-snapshot --symbol AAPL --imbalance-action-type PRE_CLOSE
```

## Futures (US only)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `futures-snapshot` | Futures snapshot | `--symbols ESM6` |
| `futures-bars` | Futures OHLCV | `--symbols ESM6 --timespan D` |
| `futures-tick` | Futures ticks | `--symbol ESM6 --count 30` |
| `futures-depth` | Order book depth | `--symbol ESM6 --depth 5` |
| `futures-footprint` | Futures order flow | `--symbols ESM6 --timespan M1` |

## Crypto (US only)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `crypto-snapshot` | Crypto snapshot | `--symbols BTCUSD` |
| `crypto-bars` | Crypto OHLCV | `--symbols BTCUSD --timespan D` |

## Event Contracts (US only)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `event-snapshot` | Event snapshot | `--symbols <sym>` |
| `event-depth` | Event depth | `--symbol <sym> --depth 5` |
| `event-bars` | Event OHLCV | `--symbols <sym> --timespan D` |
| `event-tick` | Event ticks | `--symbol <sym> --count 30` |

## Screener (US, HK, JP)

| Action | Description | Key Options |
|--------|-------------|-------------|
| `stock-gainers-losers` | Top gainers or losers by price change | `--rank-type DAY_1 --direction DESC` |
| `stock-most-active` | Most actively traded stocks | `--rank-type VOLUME` |

### `stock-gainers-losers` Options

| Option | Required | Description |
|--------|----------|-------------|
| `--rank-type` | Yes | Time period: `PRE_MARKET`, `AFTER_MARKET`, `MIN_3`, `MIN_5`, `DAY_1`, `DAY_5`, `MONTH_1`, `MONTH_3`, `WEEK_52` |
| `--category` | No | Default `US_STOCK` |
| `--sort-by` | No | Secondary sort: `CHANGE_RATIO`, `VOLUME`, `MARKET_VALUE`, `TURNOVER`, `AMPLITUDE`, etc. Default `CHANGE_RATIO` |
| `--direction` | No | `DESC` for gainers, `ASC` for losers |
| `--page-index` | No | Page number starting from 1 |
| `--page-size` | No | Records per page |

### `stock-most-active` Options

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

## Watchlist (US, HK, JP)

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

### `--instruments-json` Format

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

## Common Options

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

## Category Values

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

**SG Region (`WEBULL_REGION_ID=sg`):**

| Category | Description |
|----------|-------------|
| `US_STOCK` | US stocks (traded via SG account) |
| `US_ETF` | US ETFs (traded via SG account) |

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
