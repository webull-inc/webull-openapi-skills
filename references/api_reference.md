# Webull OpenAPI Reference

## SDK

- Package: `webull-openapi-python-sdk`
- Install: `pip3 install --upgrade webull-openapi-python-sdk`
- Repo: https://github.com/webull-inc/webull-openapi-python-sdk

## Environments & Endpoints

### US Region

| Type | Production | UAT/Test |
|------|-----------|----------|
| HTTP API | `api.webull.com` | `us-openapi-alb.uat.webullbroker.com` |
| Trading Events (gRPC) | `events-api.webull.com` | `us-openapi-events.uat.webullbroker.com` |
| Market Data (MQTT) | `data-api.webull.com` | `us-openapi-quotes-api.uat.webullbroker.com` |

### HK Region

| Type | Production | Sandbox |
|------|-----------|---------|
| HTTP API | `api.webull.hk` | `api.sandbox.webull.hk` |
| Trading Events (gRPC) | `events-api.webull.hk` | `events-api.sandbox.webull.hk` |
| Market Data (MQTT) | `data-api.webull.hk` | `data-api.sandbox.webull.hk` |

### JP Region

| Type | Production | UAT/Test |
|------|-----------|----------|
| HTTP API | `api.webull.co.jp` | `jp-openapi-alb.uat.webullbroker.com` |
| Trading Events (gRPC) | `events-api.webull.co.jp` | `jp-openapi-events.uat.webullbroker.com` |
| Market Data (MQTT) | `data-api.webull.co.jp` | `data-api.uat.webullbroker.com` |

## Feature Matrix by Region

| Feature | US | HK | JP |
|---------|----|----|-----|
| Stock trading | Yes | Yes (US/HK/CN markets) | Yes (US/JP markets) |
| Options trading | Yes | Yes (US market only) | No |
| Futures trading | Yes | No | No |
| Crypto trading | Yes | No | No |
| Event contracts | Yes | No | No |
| Combo orders (OTO/OCO/OTOCO) | Yes | No | No |
| Algo orders (TWAP/VWAP/POV) | Yes | No | No |
| Trailing stop loss | Yes | No | No |
| Fractional shares | Yes (US market) | No | No |

## Order Types by Market

### US Market
- `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TRAILING_STOP_LOSS`
- `MARKET_ON_OPEN`, `MARKET_ON_CLOSE`, `LIMIT_ON_OPEN` (institutional)

### HK Market
- `ENHANCED_LIMIT`, `AT_AUCTION`, `AT_AUCTION_LIMIT`
- BCAN (`no_party_ids`) required for institutional clients only; retail clients do not need it
- Board lot sizes vary by stock

### CN Market (A-Share via Stock Connect, HK region only)
- `LIMIT` only
- Disabled by default — contact Webull support to enable

### JP Market
- `LIMIT`, `MARKET`
- US market orders via JP: `LIMIT`, `MARKET`, `STOP_LOSS`, `STOP_LOSS_LIMIT`
- JP-specific fields: `account_tax_type` (`GENERAL`/`SPECIFIC`), `margin_type`, `position_intent`, `close_contracts`

## Time in Force

| Value | US | HK | JP |
|-------|----|----|-----|
| `DAY` | Yes | Yes | Yes (JP & US markets) |
| `GTC` | Yes | Yes | Yes (US market only) |
| `GTD` | Yes | No | No |
| `IOC` | Yes | No | No |

## Trading Sessions (US only)

| Value | Description |
|-------|-------------|
| `CORE` | Regular hours (9:30 AM - 4:00 PM ET) |
| `ALL` | Extended hours (pre-market + after-hours) |
| `NIGHT` | Night session only |

## Rate Limits

### US Region
- Auth create/check: 10 req/30s
- Market data: 600 req/min
- Order place/replace/cancel: 600 req/min
- Order query: 2 req/2s

### HK Region
- Market data: 60 req/60s
- Order place: 15 req/s (US), 1 req/s (HK/A-share)
- Order preview: 40 req/10s
- Order query: 40 req/2s

### JP Region
- Instrument lookup: 60 req/min per AppId

## Official Documentation

- US: https://developer.webull.com/apis/docs/webull-open-api-reference
- HK: https://developer.webull.hk/apis/docs/webull-open-api-reference
- JP: https://developer.webull.co.jp/apis/docs/webull-open-api-reference
- US LLM: https://developer.webull.com/apis/llms.txt
- HK LLM: https://developer.webull.hk/apis/llms.txt
- JP LLM: https://developer.webull.co.jp/apis/llms.txt
