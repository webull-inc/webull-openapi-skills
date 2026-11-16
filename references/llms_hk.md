# Source: https://developer.webull.hk/apis/llms.txt
# Fetched: 2026-11-02
# Webull HK OpenAPI Documentation

> Webull HK OpenAPI provides programmatic access to trading, market data, and brokerage services for Hong Kong, US, and China Mainland markets. Supports HTTP REST, MQTT streaming, and gRPC event subscriptions.

## Guides

### Getting Started
- [Welcome to Webull API](https://developer.webull.hk//apis/docs/docs.md): Platform overview covering Trading API, Market Data API, Broker API, and Connect API for building trading applications and brokerage solutions.
- [About Webull](https://developer.webull.hk//apis/docs/about.md): Webull company background, SFC regulatory licenses (Type 1, 2, 4), and investment philosophy.
- [About Webull OpenAPI](https://developer.webull.hk//apis/docs/about-open-api.md): OpenAPI overview — supported protocols (HTTP, MQTT, gRPC), markets (HK, US, CN), authentication model, SDKs, and AI-assisted development.
- [Getting Started](https://developer.webull.hk//apis/docs/getting-started.md): 5-step quick start — apply for API access, install SDK, get credentials, make first API call, and explore APIs.
- [SDKs and Tools](https://developer.webull.hk//apis/docs/sdk.md): Official Python & Java SDK installation, API environments (production & sandbox), shared test accounts, and management tools.
- [Additional Resources](https://developer.webull.hk//apis/docs/resources.md): SDK source code (GitHub), support channels, learning materials, and legal disclosures.

### AI-Friendly Resources
- [AI-Friendly Resources](https://developer.webull.hk//apis/docs/AI-friendly-Resources/llm.md): Machine-readable documentation (llms.txt), Markdown variants, and integration guides for Cursor, Kiro, Claude, ChatGPT, and Gemini.
- [MCP](https://developer.webull.hk//apis/docs/AI-friendly-Resources/mcp.md): Model Context Protocol integration guide for connecting AI assistants to Webull trading and market data APIs.
- [Skills](https://developer.webull.hk//apis/docs/AI-friendly-Resources/skills.md): Pre-built AI skill definitions and prompts for common Webull API workflows.

### Authentication
- [Authentication Overview](https://developer.webull.hk//apis/docs/authentication/overview.md): Dual-layer security — HMAC-SHA1 signature + Token authentication, required request headers, and credential management.
- [Trading API Application](https://developer.webull.hk//apis/docs/authentication/TradingAPIApplication.md): Step-by-step guide for individual users to apply for Trading API access and generate App Key/Secret.
- [Broker API Application](https://developer.webull.hk//apis/docs/authentication/BrokerAPIapplication.md): Institutional Broker API application, Open API Access authorization, and API key creation for portal users.
- [Signature](https://developer.webull.hk//apis/docs/authentication/signature.md): HMAC-SHA1 signature generation algorithm — request composition, worked example, edge cases (duplicate params, JSON serialization, HTML escaping), and common debugging pitfalls.
- [Token](https://developer.webull.hk//apis/docs/authentication/token.md): Token lifecycle — creation, 2FA verification via Webull App, status checks (PENDING/NORMAL/INVALID/EXPIRED), storage, and usage.

### Market Data API
- [Market Data API Overview](https://developer.webull.hk//apis/docs/market-data-api/overview.md): HTTP-based Data API and MQTT-based Data Streaming API for HK stocks, US stocks, and China A-shares.
- [Market Data API Getting Started](https://developer.webull.hk//apis/docs/market-data-api/getting-started.md): Quick start — SDK setup, fetching historical bars, and subscribing to real-time quotes with code examples.
- [Data API](https://developer.webull.hk//apis/docs/market-data-api/data-api.md): HTTP-based on-demand market data queries — snapshot, tick, quotes, historical bars for supported markets.
- [Data Streaming API](https://developer.webull.hk//apis/docs/market-data-api/data-streaming-api.md): Real-time market data streaming via MQTT protocol (v3.1.1), connection setup, subscription management, and protobuf message parsing.
- [Subscribe Advanced Quotes](https://developer.webull.hk//apis/docs/market-data-api/subscribe-quotes.md): How to purchase and activate advanced real-time market data subscriptions for OpenAPI usage.
- [Hosted Display Solution](https://developer.webull.hk//apis/docs/market-data-api/Hosted-Display-Solution.md): Display Solution framework for distributors — overview, 4-step validation process, Client-to-Server (C2S) authentication, branding guidelines, and entitlements/reporting.
- [Market Data API FAQ](https://developer.webull.hk//apis/docs/market-data-api/faq.md): Common questions about market data access, permissions, paid subscriptions, and troubleshooting.

### Trading API
- [Trading API Overview](https://developer.webull.hk//apis/docs/trade-api/overview.md): Supported markets (US, HK, A-Share), feature matrix by market, order types, trading sessions, and rate limits.
- [Trading API Getting Started](https://developer.webull.hk//apis/docs/trade-api/getting-started.md): Quick start — retrieve account list, check balances, place first order, and subscribe to order events with SDK examples.
- [Accounts](https://developer.webull.hk//apis/docs/trade-api/account.md): Account list retrieval, balance queries, and position queries via HTTP with Python and Java SDK examples.
- [Stock Trading](https://developer.webull.hk//apis/docs/trade-api/stock.md): Stock and ETF order placement — US (Limit, Market, Stop Loss, Stop Loss Limit, MOO, MOC, Fractional, Extended Hours), HK (Enhanced Limit, At-Auction, At-Auction Limit with BCAN), A-Share (Limit). Includes HK lot size notes and A-share price limit rules.
- [Options Trading](https://developer.webull.hk//apis/docs/trade-api/options.md): Options order placement — Buy/Sell Call/Put (Limit), Stop Loss, Stop Loss Limit. Sell-side only supports DAY time-in-force.
- [Futures Trading](https://developer.webull.hk//apis/docs/trade-api/futures.md): Futures trading operations and contract management.
- [Trading API FAQ](https://developer.webull.hk//apis/docs/trade-api/faq.md): Common questions about supported markets, fees, permissions, order management, signature debugging, and troubleshooting.

### Connect API
- [Connect API Getting Started](https://developer.webull.hk//apis/docs/connect-api/getting-started.md): Connect API introduction for third-party application integration (under construction).

### Broker API
- [Omnibus with Virtual Account](https://developer.webull.hk//apis/docs/broker-api/omnibus-va.md): Omnibus with Virtual Account model — business introduction, account structure, onboarding, trading products, and comparison with standard Omnibus model.
- [About Broker API](https://developer.webull.hk//apis/docs/broker-api/about-broker-api.md): Broker API introduction, capabilities, and use cases for brokerage integrations.
- [Broker API Getting Started](https://developer.webull.hk//apis/docs/broker-api/getting-started.md): Getting started guide for broker-level API integration.

### General
- [General FAQ](https://developer.webull.hk//apis/docs/faq.md): General frequently asked questions about the Webull OpenAPI platform — application, credentials, IP whitelist, A-share trading, fees, and support.

## API Reference

### Authentication — Server-To-Server
- [Create Token](https://developer.webull.hk//apis/docs/reference/create-token.md): POST /openapi/auth/token/create — Generate authentication tokens. Rate limit: 10 req/30s.
- [Check Token](https://developer.webull.hk//apis/docs/reference/check-token.md): POST /openapi/auth/token/check — Verify token validity (PENDING, NORMAL, INVALID, EXPIRED). Rate limit: 10 req/30s.

### Authentication — Client-To-Server (Display Solution)
- [Create Client Token](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/create-client-token.md): POST /openapi/auth/client/token/create — Generate access + refresh token pair for end-user applications. Rate limit: 600 req/min.
- [Refresh Client Token](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/refresh-client-token.md): POST /openapi/auth/client/token/refresh — Refresh access token using refresh token. Rate limit: 600 req/min.

### Market Data — Display Solution — Screener
- [List Top Gainers/Losers](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/top-gainers-using-get-new.md): GET /openapi/market-data/screener/rank — Top gainers/losers by change ratio, volume, market value, etc.
- [List Top Actives](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/top-active-using-get-new.md): GET — Most actively traded stocks.

### Market Data — Display Solution — Quotes
- [Snapshot (Display)](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/snapshot-using-get.md): POST /openapi/market-data/stock/snapshot — Real-time snapshot for Display Solution.
- [Historical Bars (Display)](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/query-batch-bars-using-post.md): POST — Batch historical OHLCV bars for Display Solution.
- [Tick (Display)](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/tick-using-get.md): GET — Tick-by-tick trade data for Display Solution.
- [Quotes Depth (Display)](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/quotes-using-get.md): GET — Bid/ask depth data for Display Solution.
- [Historical Bars Single Symbol (Display)](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/bars-using-get.md): GET — Historical bars for a single symbol (Display Solution).

### Market Data — Display Solution — News
- [News Summary](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/watchlist-summary-using-post.md): POST — News summary for watchlist.
- [Market News](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/list-news-by-market-using-get.md): GET — News by market.
- [Symbol News](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/list-news-by-ticker-using-get.md): GET — News by ticker symbol.
- [Latest News](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/list-latest-news-using-get.md): GET — Latest news feed.

### Market Data — Display Solution — Corporate Actions
- [Corporate Actions By Market](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/corp-market-using-get.md): GET — Corporate actions filtered by market.
- [Corporate Actions](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/corp-action-using-get.md): GET — Corporate actions by symbol.

### Market Data — Display Solution — Instrument
- [Get Instruments (Display)](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/list-using-get.md): POST — Get instrument information for Display Solution.
- [Batch Get Logos](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/batch-logo-using-post.md): POST — Batch retrieve company logos.
- [Company Profile](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/list-company-profile-using-get.md): GET — Company profile information.
- [Analyst Target Price](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/list-analyst-target-price-using-get.md): GET — Analyst target price data.
- [Analyst Rating](https://developer.webull.hk//apis/docs/reference/market-display-solution-data-api/list-analyst-rating-using-get.md): GET — Analyst rating data.

### Market Data — Non-Display Solution — Stock
- [Tick](https://developer.webull.hk//apis/docs/reference/tick.md): GET /openapi/market-data/stock/tick — Tick-by-tick trade data. Rate limit: 60 req/60s.
- [Snapshot](https://developer.webull.hk//apis/docs/reference/snapshot.md): GET /openapi/market-data/stock/snapshot — Real-time market snapshot. Rate limit: 60 req/60s.
- [Quotes](https://developer.webull.hk//apis/docs/reference/quotes.md): GET /openapi/market-data/stock/quotes — Bid/ask depth data. Rate limit: 60 req/60s.
- [Footprint](https://developer.webull.hk//apis/docs/reference/footprint.md): POST /openapi/market-data/stock/footprint — Recent N footprint records by symbol and time granularity. Rate limit: 600 req/min.
- [Historical Bars (Batch)](https://developer.webull.hk//apis/docs/reference/historical-bars.md): POST /openapi/market-data/stock/batch-bars — Batch OHLCV candlestick data. Rate limit: 60 req/60s.
- [Historical Bars (Single Symbol)](https://developer.webull.hk//apis/docs/reference/bars.md): GET /openapi/market-data/stock/bars — Single symbol OHLCV data. Rate limit: 60 req/60s.
- [NOII Bars](https://developer.webull.hk//apis/docs/reference/get-noii-bars.md): GET — Net Order Imbalance Indicator bar data for stocks.
- [NOII Snapshot](https://developer.webull.hk//apis/docs/reference/get-noii-snapshot.md): GET — Net Order Imbalance Indicator snapshot for stocks.

### Market Data — Non-Display Solution — Stock — Streaming
- [Subscribe](https://developer.webull.hk//apis/docs/reference/subscribe.md): POST /openapi/market-data/streaming/subscribe — Subscribe to real-time MQTT streams. Rate limit: 60 req/60s.
- [Unsubscribe](https://developer.webull.hk//apis/docs/reference/unsubscribe.md): POST /openapi/market-data/streaming/unsubscribe — Unsubscribe from MQTT streams. Rate limit: 60 req/60s.

### Market Data — Non-Display Solution — Futures
- [Futures Tick](https://developer.webull.hk//apis/docs/reference/futures-tick.md): GET — Tick-by-tick trade data for futures contracts.
- [Futures Snapshot](https://developer.webull.hk//apis/docs/reference/futures-snapshot.md): GET — Current futures market snapshot with latest prices and open interest.
- [Futures Footprint](https://developer.webull.hk//apis/docs/reference/futures-footprint.md): GET — Futures order flow and volume profile analysis.
- [Futures Quotes Depth](https://developer.webull.hk//apis/docs/reference/futures-depth-of-book.md): GET — Market depth data for futures contracts.
- [Futures Historical Bars](https://developer.webull.hk//apis/docs/reference/futures-historical-bars.md): GET — Historical OHLCV data for futures contracts.

### Market Data — Non-Display Solution — News
- [News Summary](https://developer.webull.hk//apis/docs/reference/news-summary.md): GET — Latest news summaries for stocks and markets.

### Market Data — Non-Display Solution — Screener
- [Stock Top Gainers/Losers Rank](https://developer.webull.hk//apis/docs/reference/get-gainers-losers.md): GET — Retrieve top gaining and losing stocks ranked by performance.
- [Top Active](https://developer.webull.hk//apis/docs/reference/get-top-active.md): GET — Retrieve most actively traded stocks by volume.
- [Market Sectors](https://developer.webull.hk//apis/docs/reference/get-market-sectors.md): GET — Retrieve market sector overview and performance rankings.
- [Market Sectors Detail](https://developer.webull.hk//apis/docs/reference/get-market-sectors-detail.md): GET — Retrieve stock list and statistics for a specific market sector.
- [High Dividend Rank](https://developer.webull.hk//apis/docs/reference/get-high-dividend.md): GET — Retrieve high dividend stocks ranking.
- [52 Week High/Low](https://developer.webull.hk//apis/docs/reference/get-week-52-high-low.md): GET — Retrieve stocks making 52-week highs or lows.

### Market Data — Non-Display Solution — Watchlist
- [Get Watchlist](https://developer.webull.hk//apis/docs/reference/get-watchlist.md): GET — Retrieve user watchlists.
- [Create Watchlist](https://developer.webull.hk//apis/docs/reference/create-watchlist.md): GET — Create a new watchlist.
- [Update Watchlist](https://developer.webull.hk//apis/docs/reference/update-watchlist.md): GET — Update an existing watchlist.
- [Delete Watchlist](https://developer.webull.hk//apis/docs/reference/delete-watchlist.md): GET — Delete a watchlist.
- [Get Watchlist Instruments](https://developer.webull.hk//apis/docs/reference/get-watchlist-instruments.md): GET — Retrieve instruments in a watchlist.
- [Add Instruments to Watchlist](https://developer.webull.hk//apis/docs/reference/add-watchlist-instruments.md): GET — Add instruments to an existing watchlist.
- [Remove Instruments from Watchlist](https://developer.webull.hk//apis/docs/reference/remove-watchlist-instruments.md): GET — Remove instruments from a watchlist.
- [Update Instruments Sort Order](https://developer.webull.hk//apis/docs/reference/update-watchlist-instruments.md): GET — Update the sort order of instruments in a watchlist.

### Market Data — Non-Display Solution — Option
- [Option Tick](https://developer.webull.hk//apis/docs/reference/option-tick.md): GET — Tick-by-tick trade data for options contracts.
- [Option Snapshot](https://developer.webull.hk//apis/docs/reference/option-snapshot.md): GET — Real-time snapshot for options contracts.
- [Option Historical Bars](https://developer.webull.hk//apis/docs/reference/option-historical-bars.md): POST — Historical OHLCV candlestick data for options contracts.

### Market Data — Non-Display Solution — Fundamentals
- [Company Profile](https://developer.webull.hk//apis/docs/reference/get-company-profile.md): GET — Retrieve company profile and fundamental information.
- [Analyst Target Price](https://developer.webull.hk//apis/docs/reference/get-analyst-target-price.md): GET — Retrieve analyst price targets for a stock.
- [Analyst Rating](https://developer.webull.hk//apis/docs/reference/get-analyst-rating.md): GET — Retrieve analyst ratings and consensus recommendations.
- [Forecast EPS](https://developer.webull.hk//apis/docs/reference/forecast-eps.md): GET — Retrieve forecast EPS and historical earnings data.
- [Filings](https://developer.webull.hk//apis/docs/reference/filings.md): GET — Retrieve SEC filings for stocks.
- [Earnings Calendar](https://developer.webull.hk//apis/docs/reference/earnings-calendar.md): GET — Retrieve earnings calendar for a stock.
- [Dividend Calendar](https://developer.webull.hk//apis/docs/reference/dividend-calendar.md): GET — Retrieve dividend calendar for a stock.
- [Capital Flow](https://developer.webull.hk//apis/docs/reference/capital-flow.md): GET — Retrieve capital flow distribution for a stock.
- [Industry Comparison](https://developer.webull.hk//apis/docs/reference/industry-comparison.md): GET — Retrieve industry peer comparison for a stock.
- [Indicators](https://developer.webull.hk//apis/docs/reference/financial-indicators.md): GET — Retrieve key financial ratios and indicators.
- [Income](https://developer.webull.hk//apis/docs/reference/financial-income.md): GET — Retrieve income statement data.
- [Cashflow](https://developer.webull.hk//apis/docs/reference/financial-cashflow.md): GET — Retrieve cash flow statement data.
- [Balancesheet](https://developer.webull.hk//apis/docs/reference/financial-balancesheet.md): GET — Retrieve balance sheet data.
- [Alert](https://developer.webull.hk//apis/docs/reference/financial-alert.md): GET — Retrieve financial alert comparing next report estimates vs last year.
- [Fund Brief](https://developer.webull.hk//apis/docs/reference/fund-brief.md): GET — Retrieve fund brief information including objective and managers.
- [Fund Performance](https://developer.webull.hk//apis/docs/reference/fund-performance.md): GET — Retrieve fund performance returns over multiple horizons.
- [Fund NetValue](https://developer.webull.hk//apis/docs/reference/fund-net-value.md): GET — Retrieve fund net asset value (NAV) history.
- [Fund Holdings](https://developer.webull.hk//apis/docs/reference/fund-holdings.md): GET — Retrieve fund top 10 holdings.
- [Fund Dividends](https://developer.webull.hk//apis/docs/reference/fund-dividends.md): GET — Retrieve fund dividend history.
- [Fund Rating](https://developer.webull.hk//apis/docs/reference/fund-rating.md): GET — Retrieve fund rating history.
- [Fund Splits](https://developer.webull.hk//apis/docs/reference/fund-splits.md): GET — Retrieve fund split history.
- [Fund Files](https://developer.webull.hk//apis/docs/reference/fund-files.md): GET — Retrieve fund documents and files.
- [Fund Allocation](https://developer.webull.hk//apis/docs/reference/fund-allocation.md): GET — Retrieve fund asset allocation by date.

### Trading API — Instrument
- [List Stock Instruments](https://developer.webull.hk//apis/docs/reference/instrument-list.md): GET /openapi/instrument/stock/list — Get profile information for instruments. Rate limit: 60 req/60s.
- [List Futures Contracts](https://developer.webull.hk//apis/docs/reference/futures-instrument-list.md): GET — Query futures contracts by symbol.
- [List Futures Product Codes](https://developer.webull.hk//apis/docs/reference/futures-products.md): GET — Available futures product categories and specifications.
- [List Futures Product Classes](https://developer.webull.hk//apis/docs/reference/futures-products-class.md): GET — Available futures product class classifications.
- [List Option Contracts](https://developer.webull.hk//apis/docs/reference/option-contract-list.md): GET — Query available option contracts for a stock.

### Trading API — Account
- [Account List](https://developer.webull.hk//apis/docs/reference/account-list.md): GET /openapi/account/list — Query account list.

### Trading API — Assets
- [Account Balance](https://developer.webull.hk//apis/docs/reference/query-account-balance.md): GET /openapi/assets/balance — Query account balance details.
- [Account Positions](https://developer.webull.hk//apis/docs/reference/query-account-position.md): GET /openapi/assets/positions — Query positions by account ID.

### Trading API — Order — Trading
- [Order Preview](https://developer.webull.hk//apis/docs/reference/common-order-preview.md): POST /openapi/trade/order/preview — Preview estimated amount and cost. Rate limit: 40 req/10s.
- [Order Place](https://developer.webull.hk//apis/docs/reference/common-order-place.md): POST /openapi/trade/order/place — Place equity and options orders. Rate limit: 15 req/s (US), 1 req/s (HK/A-share).
- [Order Replace](https://developer.webull.hk//apis/docs/reference/common-order-replace.md): POST /openapi/trade/order/replace — Modify open orders. Rate limit: 15 req/s (US), 1 req/s (HK/A-share).
- [Order Cancel](https://developer.webull.hk//apis/docs/reference/common-order-cancel.md): POST /openapi/trade/order/cancel — Cancel pending orders. Rate limit: 15 req/s (US), 1 req/s (HK/A-share).

### Trading API — Order — Order Query
- [Open Order](https://developer.webull.hk//apis/docs/reference/order-open.md): GET /openapi/trade/order/open — Query pending orders. Rate limit: 40 req/2s.
- [Order History](https://developer.webull.hk//apis/docs/reference/order-history.md): GET /openapi/trade/order/history — Query historical orders (past 7 days). Rate limit: 40 req/2s.
- [Order Detail](https://developer.webull.hk//apis/docs/reference/order-detail.md): GET /openapi/trade/order/detail — Query order details by order ID. Rate limit: 40 req/2s.
- [List Order Executions](https://developer.webull.hk//apis/docs/reference/order-execution.md): GET — List order execution records.

### Trading API — Order — Trade Events
- [Subscribe Trade Events](https://developer.webull.hk//apis/docs/reference/custom/subscribe-trade-events.md): gRPC-based real-time subscription for order status change notifications (filled, cancelled, modified, failed).
- [Subscribe Position Events](https://developer.webull.hk//apis/docs/reference/custom/subscribe-position-events.md): gRPC-based real-time subscription for position change notifications.

### Broker API — Account (ND)
- [Create Virtual Account](https://developer.webull.hk//apis/docs/reference/broker-api/broker-account-create.md): POST — Create a virtual account under the omnibus structure.
- [Update Virtual Account](https://developer.webull.hk//apis/docs/reference/broker-api/broker-account-update.md): POST — Update virtual account information.
- [Get Virtual Account Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-account-detail.md): GET — Query virtual account details.
- [List Virtual Accounts](https://developer.webull.hk//apis/docs/reference/broker-api/broker-account-list.md): GET — List all virtual accounts.

### Broker API — Instrument
- [Get Stock Instrument](https://developer.webull.hk//apis/docs/reference/broker-api/broker-instrument-list.md): GET — Query stock instrument information.
- [Get Stock Locate Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-stock-locate-detail.md): GET — Query stock locate details.
- [Get Corporate Actions Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-corporate-actions-detail.md): GET — Query corporate actions details.
- [Get Option Instrument](https://developer.webull.hk//apis/docs/reference/broker-api/broker-option-contract-list.md): GET — Query option instrument information.

### Broker API — Activities
- [Get Account Activities By Type](https://developer.webull.hk//apis/docs/reference/broker-api/broker-activity-by-type.md): GET — Query account activities filtered by type.

### Broker API — Assets
- [Account Balance](https://developer.webull.hk//apis/docs/reference/broker-api/broker-assets-balance.md): POST — Query virtual account balance.
- [Account Positions](https://developer.webull.hk//apis/docs/reference/broker-api/broker-assets-positions.md): GET — Query virtual account positions.

### Broker API — Order — Trading
- [Preview Order](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-preview.md): POST — Preview order cost and fees.
- [Place Order](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-place.md): POST — Place order on behalf of virtual account.
- [Replace Order](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-replace.md): POST — Modify an existing open order.
- [Cancel Order](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-cancel.md): POST — Cancel a pending order.

### Broker API — Order — Order Query
- [Order Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-detail.md): GET — Query order details.
- [Order History](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-history.md): GET — Query historical orders.
- [Open Order](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-open.md): GET — Query pending orders.
- [List Order Executions](https://developer.webull.hk//apis/docs/reference/broker-api/broker-order-execution.md): GET — Query order execution records.

### Broker API — Funding — FX
- [Get FX Rate](https://developer.webull.hk//apis/docs/reference/broker-api/broker-funding-query-rate.md): GET — Query foreign exchange rates.
- [Create FX Request](https://developer.webull.hk//apis/docs/reference/broker-api/broker-funding-create-fx.md): POST — Create a foreign exchange request.
- [Get FX Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-funding-query-fx.md): GET — Query FX request details.
- [Create Instant Exchange Request](https://developer.webull.hk//apis/docs/reference/broker-api/broker-funding-create-instant-fx.md): POST — Create an instant currency exchange request.
- [Get Instant Exchange Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-funding-query-instant-fx.md): GET — Query instant exchange details.

### Broker API — Funding — Instant Funding
- [Create an Instant Funding Request](https://developer.webull.hk//apis/docs/reference/broker-api/broker-funding-instant-create.md): POST — Create an instant funding request.
- [Get Instant Funding Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-funding-instant-query.md): GET — Query instant funding details.

### Broker API — Option
- [Option Exercise](https://developer.webull.hk//apis/docs/reference/broker-api/broker-option-exercise.md): POST — Submit an option exercise request.

### Broker API — Journals
- [Create Cash Journal](https://developer.webull.hk//apis/docs/reference/broker-api/broker-journal-cash-create.md): POST — Create a cash journal entry.
- [Get Cash Journal Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-journal-cash-query.md): GET — Query cash journal details.
- [Create Position Journal](https://developer.webull.hk//apis/docs/reference/broker-api/broker-journal-position-create.md): POST — Create a position journal entry.
- [Get Position Journal Detail](https://developer.webull.hk//apis/docs/reference/broker-api/broker-journal-position-query.md): GET — Query position journal details.

### Broker API — Master Data
- [Trade Calendar](https://developer.webull.hk//apis/docs/reference/broker-api/broker-trade-calendar.md): POST — Query trading calendar.

### Broker API — Events
- [Account Events](https://developer.webull.hk//apis/docs/reference/custom/broker-account-events.md): Subscription for broker account status change events.
- [Instrument Events](https://developer.webull.hk//apis/docs/reference/custom/broker-instrument-events.md): Subscription for instrument data change events.
- [Corporate Actions Events](https://developer.webull.hk//apis/docs/reference/custom/broker-ca-events.md): Subscription for corporate actions events.
- [Trade Events](https://developer.webull.hk//apis/docs/reference/custom/broker-trade-events.md): Subscription for broker trade execution events.
- [Funding Events](https://developer.webull.hk//apis/docs/reference/custom/broker-funding-events.md): Subscription for funding status change events.
- [Journal Events](https://developer.webull.hk//apis/docs/reference/custom/broker-journal-events.md): Subscription for journal entry events.
- [Master Data Events](https://developer.webull.hk//apis/docs/reference/custom/broker-master-data-events.md): Subscription for master data change events.
- [Position Events](https://developer.webull.hk//apis/docs/reference/custom/broker-position-events.md): Subscription for position change events.

## API Environments

### Production
- HTTP API: `api.webull.hk`
- Trading Events (gRPC): `events-api.webull.hk`
- Market Data Streaming (MQTT): `data-api.webull.hk`

### Sandbox
- HTTP API: `api.sandbox.webull.hk`
- Trading Events (gRPC): `events-api.sandbox.webull.hk`
- Market Data Streaming (MQTT): `data-api.sandbox.webull.hk`

### Broker API
- Production: `broker-api.webull.hk`
- Sandbox: `broker-api.sandbox.webull.hk`

### Display Solution API
- Production: `co-branding-openapi.webull.hk`
- Sandbox: `hk-co-branding-openapi.uat.webullbroker.com`

## Official SDKs

### Python
```bash
pip3 install --upgrade webull-openapi-python-sdk
```

### Java (Maven)
```xml
<dependency>
    <groupId>com.webull.openapi</groupId>
    <artifactId>webull-openapi-java-sdk</artifactId>
    <version>1.0.3</version>  <!-- Check https://central.sonatype.com/artifact/com.webull.openapi/webull-openapi-java-sdk for the latest version -->
</dependency>
```
