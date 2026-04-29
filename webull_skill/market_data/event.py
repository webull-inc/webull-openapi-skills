"""Event contract market data tools for Webull OpenAPI Skill.

Provides: get_event_tick, get_event_snapshot, get_event_depth, get_event_bars.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_event_bars,
    format_event_depth,
    format_event_snapshot,
    format_event_tick,
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


def get_event_tick(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_EVENT",
    count: int = 30,
) -> str:
    """Get event contract tick-by-tick trade data.

    Returns: time, price, volume, side.
    """
    try:
        kwargs = _build_kwargs(
            {"symbol": symbol, "category": category},
            count=count if count != 30 else None,
        )
        data = extract_response_data(sdk.data.event_market_data.get_event_tick(**kwargs))
        return prepend_disclaimer(format_event_tick(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_tick", config.region_id)


def get_event_snapshot(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_EVENT",
) -> str:
    """Get event contract real-time snapshot.

    Returns: symbol, price, change, change_ratio, volume, bid, ask.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        data = extract_response_data(
            sdk.data.event_market_data.get_event_snapshot(symbols=sym_list, category=category)
        )
        return prepend_disclaimer(format_event_snapshot(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_snapshot", config.region_id)


def get_event_depth(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_EVENT",
    depth: int = 10,
) -> str:
    """Get event contract order book depth.

    Returns: symbol, bids, asks.
    """
    try:
        kwargs = _build_kwargs(
            {"symbol": symbol, "category": category},
            depth=depth if depth != 10 else None,
        )
        data = extract_response_data(sdk.data.event_market_data.get_event_depth(**kwargs))
        return prepend_disclaimer(format_event_depth(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_depth", config.region_id)


def get_event_bars(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_EVENT",
    timespan: str = "D",
    count: int = 200,
    real_time_required: bool = False,
) -> str:
    """Get event contract OHLCV bars.

    Returns: time, open, high, low, close, volume.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs = _build_kwargs(
            {"symbols": sym_list, "timespan": timespan, "category": category},
            count=count if count != 200 else None,
            real_time_required=real_time_required,
        )
        data = extract_response_data(sdk.data.event_market_data.get_event_bars(**kwargs))
        return prepend_disclaimer(format_event_bars(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_bars", config.region_id)
