# Source: https://developer.webull-uk.com/apis/llms.txt
# Fetched: 2026-11-02
# Webull OpenAPI Documentation

## Guides

### Getting Started
- [Welcome to Webull API](https://developer.webull-uk.com/apis/docs.md): Platform overview covering trading APIs, market data services, OAuth integration, and tools for building trading applications and brokerage solutions.
- [About Webull OpenAPI](https://developer.webull-uk.com/apis/docs/about-open-api.md): OpenAPI platform capabilities and features overview.
- [Getting Started](https://developer.webull-uk.com/apis/docs/getting-started.md): Quick start guide for onboarding, API key setup, and first API call.
- [SDK & Tools](https://developer.webull-uk.com/apis/docs/sdk.md): SDK installation, development tools, and example code for trading and market data integration.
- [Additional Resources](https://developer.webull-uk.com/apis/docs/resources.md): Learning materials, blog updates, support channels, and regulatory disclosures.

### AI-Friendly Resources
- [LLM Resources](https://developer.webull-uk.com/apis/docs/ai-friendly-resources/llm.md): Machine-readable API documentation and resources optimized for LLM consumption.

### Authentication
- [Authentication Overview](https://developer.webull-uk.com/apis/docs/authentication/overview.md): Digest signature authentication using App Key and App Secret with security best practices.
- [Individual Application Process](https://developer.webull-uk.com/apis/docs/authentication/individual-application.md): Step-by-step guide for individual users to apply for API access and generate API keys.
- [Signature](https://developer.webull-uk.com/apis/docs/authentication/signature.md): HMAC-SHA1 signature generation, request composition, and required headers for API authentication.
- [Token](https://developer.webull-uk.com/apis/docs/authentication/token.md): Token lifecycle management including creation, 2FA verification, status checks, storage, and usage in API requests.

### Market Data API
- [Market Data API Overview](https://developer.webull-uk.com/apis/docs/market-data-api/overview.md): HTTP-based historical and real-time data retrieval (tick, snapshot, quotes, bars) for stocks; MQTT streaming via WebSocket/TCP; Python SDK; rate limits and subscription requirements.
- [Market Data API Getting Started](https://developer.webull-uk.com/apis/docs/market-data-api/getting-started.md): Quick start guide for SDK installation, API key setup, and requesting historical or real-time market data with code examples.
- [Data API](https://developer.webull-uk.com/apis/docs/market-data-api/data-api.md): HTTP-based market data access covering supported markets and data types.
- [Data Streaming API](https://developer.webull-uk.com/apis/docs/market-data-api/data-streaming-api.md): Real-time market data streaming via MQTT protocol implementation guide.
- [Subscribe Advanced Quotes](https://developer.webull-uk.com/apis/docs/market-data-api/subscribe-quotes.md): Browser-based guide to purchase and activate advanced real-time market data subscriptions.
- [Market Data API FAQ](https://developer.webull-uk.com/apis/docs/market-data-api/faq.md): Frequently asked questions about market data access and usage.

### Trading API
- [Trading API Overview](https://developer.webull-uk.com/apis/docs/trade-api/overview.md): Core trading functionality and capabilities overview.
- [Trading API Getting Started](https://developer.webull-uk.com/apis/docs/trade-api/getting-started.md): Quick start guide for trading API integration.
- [Trading API - Accounts](https://developer.webull-uk.com/apis/docs/trade-api/account.md): Account management, balance queries, and account information retrieval.
- [Trading API - Stock](https://developer.webull-uk.com/apis/docs/trade-api/stock.md): Stock trading operations including order placement, modification, and cancellation.
- [Trading API - FAQs](https://developer.webull-uk.com/apis/docs/trade-api/faq.md): Common questions and troubleshooting for trading API.

### General
- [Webull OpenAPI FAQs](https://developer.webull-uk.com/apis/docs/faq.md): General frequently asked questions about Webull OpenAPI platform.

## API Reference

### Authentication & Token Management
- [Create Token](https://developer.webull-uk.com/apis/docs/reference/create-token.md): Generate authentication tokens for API access.
- [Check Token](https://developer.webull-uk.com/apis/docs/reference/check-token.md): Verify token validity and status.

### Market Data - Stocks
- [Stock Tick](https://developer.webull-uk.com/apis/docs/reference/tick.md): Real-time tick-by-tick trade data for stocks.
- [Stock Snapshot](https://developer.webull-uk.com/apis/docs/reference/snapshot.md): Current market snapshot with latest prices and statistics.
- [Stock Quotes](https://developer.webull-uk.com/apis/docs/reference/quotes.md): Real-time bid/ask quotes and market depth.
- [Stock Footprint](https://developer.webull-uk.com/apis/docs/reference/footprint.md): Order flow and volume profile analysis data.
- [Stock Historical Bars](https://developer.webull-uk.com/apis/docs/reference/historical-bars.md): Historical OHLCV candlestick data for multiple symbols.
- [Stock Historical Bars (Single Symbol)](https://developer.webull-uk.com/apis/docs/reference/bars.md): Historical OHLCV candlestick data for a single symbol.

### Market Data - Streaming
- [Subscribe Events](https://developer.webull-uk.com/apis/docs/reference/subscribe.md): Subscribe to real-time market data streams via MQTT.
- [Unsubscribe Events](https://developer.webull-uk.com/apis/docs/reference/unsubscribe.md): Unsubscribe from real-time market data streams.

### Instruments & Symbols
- [Stock Instruments](https://developer.webull-uk.com/apis/docs/reference/instrument-list.md): List of available stock symbols and instrument details.

### Account Management
- [Account List](https://developer.webull-uk.com/apis/docs/reference/account-list.md): Retrieve list of user accounts and account IDs.
- [Account Balance](https://developer.webull-uk.com/apis/docs/reference/account-balance.md): Query account balance, buying power, and cash details.
- [Account Positions](https://developer.webull-uk.com/apis/docs/reference/account-position.md): Retrieve current positions and holdings.

### Order Management - Trading
- [Preview Order](https://developer.webull-uk.com/apis/docs/reference/common-order-preview.md): Preview order details and estimated costs before placement.
- [Place Order](https://developer.webull-uk.com/apis/docs/reference/common-order-place.md): Submit new orders for stocks.
- [Replace Order](https://developer.webull-uk.com/apis/docs/reference/common-order-replace.md): Modify existing open orders (price, quantity, etc.).
- [Cancel Order](https://developer.webull-uk.com/apis/docs/reference/common-order-cancel.md): Cancel pending or open orders.

### Order Management - Query
- [Order History](https://developer.webull-uk.com/apis/docs/reference/order-history.md): Query historical order records and execution details.
- [Open Orders](https://developer.webull-uk.com/apis/docs/reference/order-open.md): Retrieve list of current open orders.
- [Order Detail](https://developer.webull-uk.com/apis/docs/reference/order-detail.md): Get detailed information for a specific order.

### Trade Events
- [Subscribe Trade Events](https://developer.webull-uk.com/apis/docs/reference/custom/subscribe-trade-events.md): Subscribe to real-time trade execution and order status events via WebSocket.

## Changelog
- [Documentation Changelog](https://developer.webull-uk.com/apis/docs/changelog.md): Track updates, new features, and changes to the API documentation.

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
    <version>1.0.3</version>
</dependency>
```
