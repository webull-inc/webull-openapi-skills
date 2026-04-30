"""Futures market data tools for Webull OpenAPI Skill.

Provides: get_futures_tick, get_futures_snapshot, get_futures_depth,
          get_futures_bars, get_futures_footprint.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_futures_bars,
    format_futures_depth,
    format_futures_footprint,
    format_futures_snapshot,
    format_futures_tick,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


def _build_kwargs(base: dict[str, Any], **optional: Any) -> dict[str, Any]:
    """Build kwargs dict, adding only non-None / truthy optional values."""
    for key, value in optional.items():
        if value is not None and value is not False:
            base[key] = value
    return base


def get_futures_tick(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_FUTURES",
    count: int = 200,
) -> str:
    """Get futures tick-by-tick trade data.

    Returns: time, price, volume, side.
    """
    try:
        kwargs = _build_kwargs(
            {"symbol": symbol, "category": category},
            count=str(count) if count != 200 else None,
        )
        data = extract_response_data(sdk.data.futures_market_data.get_futures_tick(**kwargs))
        return prepend_disclaimer(format_futures_tick(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_tick", config.region_id)


def get_futures_snapshot(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_FUTURES",
) -> str:
    """Get futures real-time snapshot.

    Returns: symbol, price, change, change_ratio, volume,
    open_interest, settle_price, bid, ask.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        data = extract_response_data(
            sdk.data.futures_market_data.get_futures_snapshot(symbols=sym_list, category=category)
        )
        return prepend_disclaimer(format_futures_snapshot(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_snapshot", config.region_id)


def get_futures_depth(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_FUTURES",
    depth: Optional[int] = None,
) -> str:
    """Get futures order book depth.

    Returns: symbol, bids, asks.
    """
    try:
        kwargs = _build_kwargs(
            {"symbol": symbol, "category": category},
            depth=depth,
        )
        data = extract_response_data(sdk.data.futures_market_data.get_futures_depth(**kwargs))
        return prepend_disclaimer(format_futures_depth(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_depth", config.region_id)


def get_futures_bars(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_FUTURES",
    timespan: str = "D",
    count: int = 200,
    real_time_required: bool = False,
) -> str:
    """Get futures OHLCV bars in batch.

    Returns: time, open, high, low, close, volume.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs = _build_kwargs(
            {"symbols": sym_list, "category": category, "timespan": timespan},
            count=str(count) if count != 200 else None,
            real_time_required=real_time_required,
        )
        data = extract_response_data(sdk.data.futures_market_data.get_futures_history_bars(**kwargs))
        return prepend_disclaimer(format_futures_bars(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_bars", config.region_id)


def get_futures_footprint(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_FUTURES",
    timespan: str = "M1",
    count: int = 200,
    real_time_required: bool = False,
    trading_sessions: Optional[str] = None,
) -> str:
    """Get futures large order footprint (order flow).

    Returns: time, trading_session, total, delta, buy_total, sell_total.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs = _build_kwargs(
            {"symbols": sym_list, "category": category, "timespan": timespan},
            count=str(count) if count != 200 else None,
            real_time_required=real_time_required,
            trading_sessions=trading_sessions,
        )
        data = extract_response_data(sdk.data.futures_market_data.get_futures_footprint(**kwargs))
        return prepend_disclaimer(format_futures_footprint(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_footprint", config.region_id)
