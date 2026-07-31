"""Option market data tools for Webull OpenAPI Skill.

Provides: get_option_tick, get_option_snapshot, get_option_bars.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_option_bars,
    format_option_snapshot,
    format_option_tick,
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


def get_option_tick(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_OPTION",
    count: int = 30,
) -> str:
    """Get option tick-by-tick trade data.

    Returns: time, price, volume, side.
    """
    try:
        data = extract_response_data(
            sdk.data.option_market_data.get_option_tick(
                symbol=symbol, category=category, count=str(count),
            )
        )
        return prepend_disclaimer(format_option_tick(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_option_tick", config.region_id)


def get_option_snapshot(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_OPTION",
) -> str:
    """Get real-time option snapshot. Supports multiple option symbols (max 20).

    Option symbol format: e.g. AAPL260522C00300000
    Returns: symbol, price, change, change_ratio, volume, bid, ask, open_interest, greeks.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        data = extract_response_data(
            sdk.data.option_market_data.get_option_snapshot(
                symbols=sym_list, category=category,
            )
        )
        return prepend_disclaimer(format_option_snapshot(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_option_snapshot", config.region_id)


def get_option_bars(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_OPTION",
    timespan: str = "D",
    count: int = 200,
    real_time_required: bool = False,
) -> str:
    """Get option OHLCV bars in batch.

    Option symbol format: e.g. AAPL260522C00300000
    Returns: time, open, high, low, close, volume.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs = _build_kwargs(
            {"symbols": sym_list, "category": category, "timespan": timespan},
            count=str(count) if count != 200 else None,
            real_time_required=real_time_required,
        )
        data = extract_response_data(
            sdk.data.option_market_data.get_option_history_bars(**kwargs)
        )
        return prepend_disclaimer(format_option_bars(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_option_bars", config.region_id)
