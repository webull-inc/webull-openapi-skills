"""Stock screener tools for Webull OpenAPI Skill.

Provides: get_gainers_losers, get_most_active.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_gainers_losers,
    format_most_active,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


def get_gainers_losers(
    sdk: "SDKClient",
    config: "SkillConfig",
    rank_type: str,
    category: str = "US_STOCK",
    sort_by: str = "CHANGE_RATIO",
    direction: Optional[str] = None,
    page_index: Optional[int] = None,
    page_size: Optional[int] = None,
) -> str:
    """Get top gainers or losers ranked by price change percentage.

    Use direction='DESC' for gainers, direction='ASC' for losers.

    :param rank_type: Time period. Values: PRE_MARKET, AFTER_MARKET, MIN_3,
        MIN_5, DAY_1, DAY_5, MONTH_1, MONTH_3, WEEK_52.
    :param category: Security category, e.g. US_STOCK.
    :param sort_by: Secondary sort field. Values: CHANGE_RATIO,
        RELATIVE_VOLUME_10D, MARKET_VALUE, CLOSE, PRICE, PE_TTM,
        HIGH, LOW, AMPLITUDE, TURNOVER, VOLUME.
    :param direction: ASC (losers) or DESC (gainers).
    :param page_index: Page number starting from 1.
    :param page_size: Records per page.
    Returns: instrument_id, symbol, name, exchange_code, currency_code, price,
        pre_close, open, high, low, close, change, change_ratio, volume,
        turnover, turnover_rate, market_value, amplitude.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.get_gainers_losers(
                rank_type=rank_type,
                category=category,
                sort_by=sort_by,
                direction=direction,
                page_index=page_index,
                page_size=page_size,
            )
        )
        return prepend_disclaimer(format_gainers_losers(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_gainers_losers", config.region_id)


def get_most_active(
    sdk: "SDKClient",
    config: "SkillConfig",
    category: str = "US_STOCK",
    rank_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    direction: Optional[str] = None,
    page_index: Optional[int] = None,
    page_size: Optional[int] = None,
) -> str:
    """Get most actively traded stocks ranked by volume or other activity metrics.

    Default sort: rank_type=VOLUME, sort_by=VOLUME, direction=DESC.

    :param category: Security category, e.g. US_STOCK.
    :param rank_type: Activity metric. Values: VOLUME, RELATIVE_VOLUME_10D,
        TURNOVER, TURNOVER_RATE, AMPLITUDE.
    :param sort_by: Secondary sort field. Values: CHANGE_RATIO,
        RELATIVE_VOLUME_10D, MARKET_VALUE, CLOSE, PRICE, PE_TTM,
        HIGH, LOW, AMPLITUDE, TURNOVER, VOLUME.
    :param direction: ASC or DESC (default DESC).
    :param page_index: Page number starting from 1.
    :param page_size: Records per page.
    Returns: instrument_id, symbol, name, exchange_code, currency_code, price,
        pre_close, open, high, low, close, change, change_ratio, volume,
        turnover, turnover_rate, market_value, amplitude, relative_volume_10d.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.get_most_active(
                category=category,
                rank_type=rank_type,
                sort_by=sort_by,
                direction=direction,
                page_index=page_index,
                page_size=page_size,
            )
        )
        return prepend_disclaimer(format_most_active(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_most_active", config.region_id)
