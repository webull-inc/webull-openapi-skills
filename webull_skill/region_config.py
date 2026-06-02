"""Region-specific configuration for Webull OpenAPI Skill.

Defines region configurations for US, HK, and JP markets with:
- Feature flags (futures, crypto, event contracts, etc.)
- Valid enum sets for order types, time-in-force, trading sessions, etc.

Note: API endpoints are handled by the SDK (production) or sdk_client.py (UAT).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegionConfig:
    """Immutable region-specific configuration."""

    region_id: str  # "us" | "hk" | "jp"

    # Feature flags
    supports_futures: bool
    supports_crypto: bool
    supports_event_contracts: bool
    supports_combo_orders: bool
    supports_option_strategies: bool
    supports_algo_orders: bool

    # Valid enum values for this region
    valid_order_types: frozenset[str]
    valid_time_in_force: frozenset[str]
    valid_trading_sessions: frozenset[str]
    valid_combo_types: frozenset[str]
    valid_option_strategies: frozenset[str]
    valid_order_markets: frozenset[str]
    valid_market_categories: frozenset[str]
    valid_order_types_by_market: dict[str, frozenset[str]] | None = None
    valid_time_in_force_by_market: dict[str, frozenset[str]] | None = None


# =============================================================================
# US Region Configuration
# =============================================================================
US_REGION_CONFIG = RegionConfig(
    region_id="us",
    supports_futures=True,
    supports_crypto=True,
    supports_event_contracts=True,
    supports_combo_orders=True,
    supports_option_strategies=True,
    supports_algo_orders=True,
    valid_order_types=frozenset({
        "LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT",
        "TRAILING_STOP_LOSS", "MARKET_ON_OPEN", "MARKET_ON_CLOSE", "LIMIT_ON_OPEN"
    }),
    valid_time_in_force=frozenset({"DAY", "GTC", "IOC"}),
    valid_trading_sessions=frozenset({"ALL", "CORE", "NIGHT"}),
    valid_combo_types=frozenset({
        "NORMAL", "MASTER", "STOP_PROFIT", "STOP_LOSS", "OTO", "OCO", "OTOCO"
    }),
    valid_option_strategies=frozenset({
        "SINGLE", "COVERED_STOCK", "STRADDLE", "STRANGLE", "VERTICAL",
        "CALENDAR", "BUTTERFLY", "CONDOR", "COLLAR_WITH_STOCK",
        "IRON_BUTTERFLY", "IRON_CONDOR", "DIAGONAL"
    }),
    valid_order_markets=frozenset({"US"}),
    valid_market_categories=frozenset({"US_STOCK", "US_ETF"}),
)


# =============================================================================
# HK Region Configuration
# =============================================================================
HK_REGION_CONFIG = RegionConfig(
    region_id="hk",
    supports_futures=True,
    supports_crypto=False,
    supports_event_contracts=False,
    supports_combo_orders=False,
    supports_option_strategies=False,
    supports_algo_orders=False,
    valid_order_types=frozenset({
        "LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT",
        "ENHANCED_LIMIT", "AT_AUCTION", "AT_AUCTION_LIMIT", "MARKET_ON_OPEN"
    }),
    valid_time_in_force=frozenset({"DAY", "GTD", "GTC"}),
    valid_trading_sessions=frozenset({"CORE", "ALL_DAY", "NIGHT", "ALL"}),
    valid_combo_types=frozenset({"NORMAL"}),
    valid_option_strategies=frozenset({"SINGLE"}),
    valid_order_markets=frozenset({"US", "HK", "CN"}),
    valid_market_categories=frozenset({"US", "HK", "CN"}),
    valid_time_in_force_by_market={
        "CN": frozenset({"DAY"}),
        "HK": frozenset({"DAY", "GTC"}),
        "US": frozenset({"DAY", "GTC", "GTD"}),
    },
)


# =============================================================================
# JP Region Configuration
# =============================================================================
JP_REGION_CONFIG = RegionConfig(
    region_id="jp",
    supports_futures=False,
    supports_crypto=False,
    supports_event_contracts=False,
    supports_combo_orders=False,
    supports_option_strategies=False,
    supports_algo_orders=False,
    valid_order_types=frozenset({
        "LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"
    }),
    valid_time_in_force=frozenset({"DAY", "GTC"}),
    valid_trading_sessions=frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"}),
    valid_combo_types=frozenset({"NORMAL"}),
    valid_option_strategies=frozenset({"SINGLE"}),
    valid_order_markets=frozenset({"US", "JP"}),
    valid_market_categories=frozenset({"US_STOCK", "US_ETF"}),
    valid_order_types_by_market={
        "JP": frozenset({"LIMIT", "MARKET"}),
        "US": frozenset({"LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"}),
    },
    valid_time_in_force_by_market={
        "JP": frozenset({"DAY"}),
        "US": frozenset({"DAY", "GTC"}),
    },
)


# =============================================================================
# SG Region Configuration
# =============================================================================
SG_REGION_CONFIG = RegionConfig(
    region_id="sg",
    supports_futures=False,
    supports_crypto=False,
    supports_event_contracts=False,
    supports_combo_orders=False,
    supports_option_strategies=False,
    supports_algo_orders=False,
    valid_order_types=frozenset({
        "LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"
    }),
    valid_time_in_force=frozenset({"DAY", "GTC"}),
    valid_trading_sessions=frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"}),
    valid_combo_types=frozenset({"NORMAL"}),
    valid_option_strategies=frozenset({"SINGLE"}),
    valid_order_markets=frozenset({"US"}),
    valid_market_categories=frozenset({"US_STOCK", "US_ETF"}),
)


# =============================================================================
# TH Region Configuration
# =============================================================================
TH_REGION_CONFIG = RegionConfig(
    region_id="th",
    supports_futures=False,
    supports_crypto=False,
    supports_event_contracts=False,
    supports_combo_orders=False,
    supports_option_strategies=False,
    supports_algo_orders=False,
    valid_order_types=frozenset({
        "LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"
    }),
    valid_time_in_force=frozenset({"DAY", "GTC"}),
    valid_trading_sessions=frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"}),
    valid_combo_types=frozenset({"NORMAL"}),
    valid_option_strategies=frozenset({"SINGLE"}),
    valid_order_markets=frozenset({"US"}),
    valid_market_categories=frozenset({"US_STOCK", "US_ETF"}),
)


# =============================================================================
# MY Region Configuration
# =============================================================================
MY_REGION_CONFIG = RegionConfig(
    region_id="my",
    supports_futures=False,
    supports_crypto=False,
    supports_event_contracts=False,
    supports_combo_orders=False,
    supports_option_strategies=False,
    supports_algo_orders=False,
    valid_order_types=frozenset({
        "LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"
    }),
    valid_time_in_force=frozenset({"DAY", "GTC"}),
    valid_trading_sessions=frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"}),
    valid_combo_types=frozenset({"NORMAL"}),
    valid_option_strategies=frozenset({"SINGLE"}),
    valid_order_markets=frozenset({"US"}),
    valid_market_categories=frozenset({"US_STOCK", "US_ETF"}),
)


# =============================================================================
# UK Region Configuration
# =============================================================================
UK_REGION_CONFIG = RegionConfig(
    region_id="uk",
    supports_futures=False,
    supports_crypto=False,
    supports_event_contracts=False,
    supports_combo_orders=False,
    supports_option_strategies=False,
    supports_algo_orders=False,
    valid_order_types=frozenset({
        "LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"
    }),
    valid_time_in_force=frozenset({"DAY", "GTC"}),
    valid_trading_sessions=frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"}),
    valid_combo_types=frozenset({"NORMAL"}),
    valid_option_strategies=frozenset({"SINGLE"}),
    valid_order_markets=frozenset({"US"}),
    valid_market_categories=frozenset({"US_STOCK", "US_ETF"}),
)


# =============================================================================
# Region Configuration Registry
# =============================================================================
REGION_CONFIGS: dict[str, RegionConfig] = {
    "us": US_REGION_CONFIG,
    "hk": HK_REGION_CONFIG,
    "jp": JP_REGION_CONFIG,
    "sg": SG_REGION_CONFIG,
    "th": TH_REGION_CONFIG,
    "my": MY_REGION_CONFIG,
    "uk": UK_REGION_CONFIG,
}

SUPPORTED_REGIONS: frozenset[str] = frozenset(REGION_CONFIGS.keys())


def get_region_config(region_id: str) -> RegionConfig:
    """Get region configuration by ID.

    Parameters
    ----------
    region_id
        Region identifier (us, hk, jp). Case-insensitive.

    Returns
    -------
    RegionConfig
        The region configuration for the specified region.

    Raises
    ------
    UnsupportedRegionError
        If the region ID is not supported.
    """
    from webull_skill.errors import UnsupportedRegionError

    config = REGION_CONFIGS.get(region_id.lower())
    if config is None:
        raise UnsupportedRegionError(region_id, sorted(SUPPORTED_REGIONS))
    return config
