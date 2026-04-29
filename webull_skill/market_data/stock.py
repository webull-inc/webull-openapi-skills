"""Stock market data tools for Webull OpenAPI Skill.

Provides: get_stock_tick, get_stock_snapshot, get_stock_quotes,
          get_stock_footprint, get_stock_bars, get_stock_bars_single.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_stock_bars,
    format_stock_footprint,
    format_stock_quotes,
    format_stock_snapshot,
    format_stock_tick,
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


def get_stock_tick(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    count: int = 30,
    trading_sessions: Optional[str] = None,
) -> str:
    """Get stock tick-by-tick trade data.

    Returns: time, price, volume, side, trading_session.
    """
    try:
        kwargs = _build_kwargs(
            {"symbol": symbol, "category": category, "count": str(count)},
            trading_sessions=trading_sessions,
        )
        data = extract_response_data(sdk.data.market_data.get_tick(**kwargs))
        return prepend_disclaimer(format_stock_tick(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_tick", config.region_id)


def get_stock_snapshot(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_STOCK",
    extend_hour_required: bool = False,
    overnight_required: bool = False,
) -> str:
    """Get real-time stock/ETF snapshot. Supports multiple symbols.

    Returns: symbol, price, pre_close, open, high, low, close, volume,
    change, change_ratio, bid, ask, extend_hour, overnight data.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs = _build_kwargs(
            {"symbols": sym_list, "category": category},
            extend_hour_required=extend_hour_required,
            overnight_required=overnight_required,
        )
        data = extract_response_data(sdk.data.market_data.get_snapshot(**kwargs))
        return prepend_disclaimer(format_stock_snapshot(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_snapshot", config.region_id)


def get_stock_quotes(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    depth: Optional[int] = None,
    overnight_required: bool = False,
) -> str:
    """Get real-time stock bid/ask quotes with depth. Single symbol only.

    Returns: symbol, bid_price, bid_size, ask_price, ask_size.
    """
    try:
        kwargs = _build_kwargs(
            {"symbol": symbol, "category": category},
            depth=depth,
            overnight_required=overnight_required,
        )
        data = extract_response_data(sdk.data.market_data.get_quotes(**kwargs))
        return prepend_disclaimer(format_stock_quotes(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_quotes", config.region_id)


def get_stock_footprint(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_STOCK",
    timespan: str = "M1",
    count: int = 200,
    real_time_required: bool = False,
    trading_sessions: Optional[str] = None,
) -> str:
    """Get stock large order footprint (order flow). US_STOCK only.

    Returns: time, trading_session, total, delta, buy_total, sell_total,
    buy_detail, sell_detail.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs = _build_kwargs(
            {"symbols": sym_list, "category": category, "timespan": timespan, "count": str(count)},
            real_time_required=real_time_required,
            trading_sessions=trading_sessions,
        )
        data = extract_response_data(sdk.data.market_data.get_footprint(**kwargs))
        return prepend_disclaimer(format_stock_footprint(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_footprint", config.region_id)


def get_stock_bars(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_STOCK",
    timespan: str = "D",
    count: int = 200,
    real_time_required: bool = False,
    trading_sessions: Optional[str] = None,
) -> str:
    """Get stock OHLCV bars in batch. Supports multiple symbols.

    Returns: time, open, high, low, close, volume.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs = _build_kwargs(
            {"symbols": sym_list, "category": category, "timespan": timespan, "count": str(count)},
            real_time_required=real_time_required,
            trading_sessions=trading_sessions,
        )
        data = extract_response_data(sdk.data.market_data.get_batch_history_bar(**kwargs))
        return prepend_disclaimer(format_stock_bars(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_bars", config.region_id)


def get_stock_bars_single(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    timespan: str = "D",
    count: int = 200,
    real_time_required: bool = False,
    trading_sessions: Optional[str] = None,
) -> str:
    """Get OHLCV bars for a single stock.

    Returns: time, open, high, low, close, volume.
    """
    try:
        kwargs = _build_kwargs(
            {"symbol": symbol, "category": category, "timespan": timespan, "count": str(count)},
            real_time_required=real_time_required,
            trading_sessions=trading_sessions,
        )
        data = extract_response_data(sdk.data.market_data.get_history_bar(**kwargs))
        return prepend_disclaimer(format_stock_bars(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_bars_single", config.region_id)
