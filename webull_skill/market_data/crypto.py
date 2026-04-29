"""Crypto market data tools for Webull OpenAPI Skill.

Provides: get_crypto_snapshot, get_crypto_bars.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_crypto_bars,
    format_crypto_snapshot,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


def get_crypto_snapshot(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_CRYPTO",
) -> str:
    """Get cryptocurrency real-time snapshot.

    Returns: symbol, price, change, change_ratio, bid, ask.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        data = extract_response_data(
            sdk.data.crypto_market_data.get_crypto_snapshot(symbols=sym_list, category=category)
        )
        return prepend_disclaimer(format_crypto_snapshot(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_crypto_snapshot", config.region_id)


def get_crypto_bars(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbols: str,
    category: str = "US_CRYPTO",
    timespan: str = "D",
    count: int = 200,
    real_time_required: bool = False,
) -> str:
    """Get cryptocurrency OHLCV bars.

    Returns: time, open, high, low, close, volume.
    """
    try:
        sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
        kwargs: dict[str, Any] = {"symbols": sym_list, "category": category, "timespan": timespan}
        if count != 200:
            kwargs["count"] = str(count)
        if real_time_required:
            kwargs["real_time_required"] = real_time_required
        data = extract_response_data(
            sdk.data.crypto_market_data.get_crypto_history_bar(**kwargs)
        )
        return prepend_disclaimer(format_crypto_bars(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_crypto_bars", config.region_id)
