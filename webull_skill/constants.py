"""Enum constants used throughout the Webull OpenAPI Skill."""

from __future__ import annotations

# Trading sides
VALID_SIDES: frozenset[str] = frozenset({"BUY", "SELL", "SHORT"})

# Stock/crypto/futures order types
VALID_ORDER_TYPES: frozenset[str] = frozenset({
    "MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TRAILING_STOP_LOSS",
})

# Option order types (subset of stock order types)
VALID_OPTION_ORDER_TYPES: frozenset[str] = frozenset({
    "MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT",
})

# Time-in-force for option orders (subset)
VALID_OPTION_TIF: frozenset[str] = frozenset({"DAY", "GTC"})

# Entrust (order quantity) types
VALID_ENTRUST_TYPES: frozenset[str] = frozenset({"QTY", "AMOUNT"})

# Trading session types
VALID_TRADING_SESSIONS: frozenset[str] = frozenset({"ALL", "CORE", "NIGHT"})

# Option types
VALID_OPTION_TYPES: frozenset[str] = frozenset({"CALL", "PUT"})

# Stock categories
VALID_STOCK_CATEGORIES: frozenset[str] = frozenset({"US_STOCK", "US_ETF"})

# K-line timeframes for stocks
VALID_TIMEFRAMES: frozenset[str] = frozenset({
    "1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w",
})

# K-line timeframes for crypto
VALID_CRYPTO_TIMEFRAMES: frozenset[str] = frozenset({
    "1m", "5m", "1h", "4h", "1d",
})

# Option strategies
VALID_OPTION_STRATEGIES: frozenset[str] = frozenset({
    "SINGLE", "COVERED_STOCK", "STRADDLE", "STRANGLE", "VERTICAL",
    "CALENDAR", "BUTTERFLY", "CONDOR", "COLLAR_WITH_STOCK",
    "IRON_BUTTERFLY", "IRON_CONDOR", "DIAGONAL",
})

# Min/max leg count per option strategy
STRATEGY_LEG_COUNT: dict[str, tuple[int, int]] = {
    "SINGLE": (1, 1),
    "COVERED_STOCK": (2, 2),
    "STRADDLE": (2, 2),
    "STRANGLE": (2, 2),
    "VERTICAL": (2, 2),
    "CALENDAR": (2, 2),
    "BUTTERFLY": (3, 4),
    "CONDOR": (4, 4),
    "COLLAR_WITH_STOCK": (3, 3),
    "IRON_BUTTERFLY": (4, 4),
    "IRON_CONDOR": (4, 4),
    "DIAGONAL": (2, 2),
}


# =============================================================================
# Account label to asset type mapping (US region)
# =============================================================================

# Account labels that support stock and option trading
STOCK_OPTION_ACCOUNT_LABELS: frozenset[str] = frozenset({
    "Individual Cash",
    "Individual Margin",
    "Individual US Margin",
    "Roth IRA",
    "Traditional IRA",
    "Rollover IRA",
    "Managed Roth IRA",
    "Managed Traditional IRA",
})

# Account labels for specific asset types
FUTURES_ACCOUNT_LABEL = "Futures"
CRYPTO_ACCOUNT_LABEL = "Crypto"
EVENT_ACCOUNT_LABEL = "Events Cash"

# Mapping from order asset type to valid account labels
ASSET_TYPE_ACCOUNT_LABELS: dict[str, frozenset[str]] = {
    "stock": STOCK_OPTION_ACCOUNT_LABELS,
    "option": STOCK_OPTION_ACCOUNT_LABELS,
    "futures": frozenset({FUTURES_ACCOUNT_LABEL}),
    "crypto": frozenset({CRYPTO_ACCOUNT_LABEL}),
    "event": frozenset({EVENT_ACCOUNT_LABEL}),
}

# JP account and order extension values
JP_STOCK_ACCOUNT_TYPES: frozenset[str] = frozenset({"CASH", "US_MARGIN"})
JP_MARGIN_ACCOUNT_TYPE = "US_MARGIN"
JP_CASH_ACCOUNT_TYPE = "CASH"

JP_ACCOUNT_TAX_TYPES: frozenset[str] = frozenset({"GENERAL", "SPECIFIC"})
JP_MARGIN_TYPES: frozenset[str] = frozenset({"ONE_DAY", "INDEFINITE"})
JP_POSITION_INTENTS: frozenset[str] = frozenset({
    "BUY_TO_OPEN",
    "BUY_TO_CLOSE",
    "SELL_TO_OPEN",
    "SELL_TO_CLOSE",
})
JP_MAX_CLOSE_CONTRACTS = 10
