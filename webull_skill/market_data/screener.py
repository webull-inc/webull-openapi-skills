"""Stock screener tools for Webull OpenAPI Skill.

Provides: get_gainers_losers, get_most_active, get_market_sectors,
          get_market_sectors_detail, get_high_dividend, get_52whl.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_gainers_losers,
    format_most_active,
    format_market_sectors,
    format_market_sectors_detail,
    format_high_dividend,
    format_52whl,
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


def get_market_sectors(
    sdk: "SDKClient",
    config: "SkillConfig",
    category: str = "US_STOCK",
    agg_type: Optional[str] = None,
    period: Optional[str] = None,
    page_index: Optional[int] = None,
    page_size: Optional[int] = None,
    direction: Optional[str] = None,
) -> str:
    """Get all sector overview data.

    :param category: Security category, e.g. US_STOCK.
    :param agg_type: Statistics type. Default MARKET_VALUE. Enum: MARKET_VALUE, VOLUME.
    :param period: Statistics period. Default D1. Enum: D1, D5, M01, M03.
    :param page_index: Page number starting from 1.
    :param page_size: Records per page.
    :param direction: Sort direction: ASC or DESC.
    Returns: sector overview list.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.get_market_sectors(
                category=category,
                agg_type=agg_type,
                period=period,
                page_index=page_index,
                page_size=page_size,
                direction=direction,
            )
        )
        return prepend_disclaimer(format_market_sectors(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_market_sectors", config.region_id)


def get_market_sectors_detail(
    sdk: "SDKClient",
    config: "SkillConfig",
    sector_id: str,
    category: str = "US_STOCK",
    period: Optional[str] = None,
    page_index: Optional[int] = None,
    page_size: Optional[int] = None,
    sort_by: Optional[str] = None,
    direction: Optional[str] = None,
) -> str:
    """Get stock list and statistics for a specific sector.

    :param sector_id: Sector ID. Required.
    :param category: Security category, e.g. US_STOCK.
    :param period: Statistics period. Default D1. Enum: D1, D5, M01, M03.
    :param page_index: Page number starting from 1.
    :param page_size: Records per page.
    :param sort_by: Sort field. Default CHANGE_RATIO.
    :param direction: Sort direction: ASC or DESC.
    Returns: sector detail with stock list.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.get_market_sectors_detail(
                sector_id=sector_id,
                category=category,
                period=period,
                page_index=page_index,
                page_size=page_size,
                sort_by=sort_by,
                direction=direction,
            )
        )
        return prepend_disclaimer(format_market_sectors_detail(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_market_sectors_detail", config.region_id)


def get_high_dividend(
    sdk: "SDKClient",
    config: "SkillConfig",
    category: str = "US_STOCK",
    sort_by: Optional[str] = None,
    page_index: Optional[int] = None,
    page_size: Optional[int] = None,
    direction: Optional[str] = None,
) -> str:
    """Get high dividend rank list.

    :param category: Security category, e.g. US_STOCK.
    :param sort_by: Sort field. Default YIELD.
    :param page_index: Page number starting from 1.
    :param page_size: Records per page.
    :param direction: Sort direction: ASC or DESC.
    Returns: high dividend stocks.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.get_high_dividend(
                category=category,
                sort_by=sort_by,
                page_index=page_index,
                page_size=page_size,
                direction=direction,
            )
        )
        return prepend_disclaimer(format_high_dividend(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_high_dividend", config.region_id)


def get_52whl(
    sdk: "SDKClient",
    config: "SkillConfig",
    category: str = "US_STOCK",
    rank_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    page_index: Optional[int] = None,
    page_size: Optional[int] = None,
    direction: Optional[str] = None,
) -> str:
    """Get 52-week high/low rank list.

    :param category: Security category, e.g. US_STOCK.
    :param rank_type: Index code. Enum: NEW_HIGH, NEAR_HIGH, NEW_LOW, NEAR_LOW.
    :param sort_by: Sort field. Default CHANGE_RATIO_52W.
    :param page_index: Page number starting from 1.
    :param page_size: Records per page.
    :param direction: Sort direction: ASC or DESC.
    Returns: 52-week high/low stocks.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.get_52whl(
                category=category,
                rank_type=rank_type,
                sort_by=sort_by,
                page_index=page_index,
                page_size=page_size,
                direction=direction,
            )
        )
        return prepend_disclaimer(format_52whl(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_52whl", config.region_id)
