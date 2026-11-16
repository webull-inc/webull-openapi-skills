"""Stock screener tools for Webull OpenAPI Skill.

Provides: get_gainers_losers, get_most_active, get_market_sectors,
          get_market_sectors_detail, get_high_dividend, get_52whl,
          get_market_sentiment, get_stock_unusual_activities.
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
    format_market_sentiment,
    format_stock_unusual_activities,
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
    Returns: instrument_id, symbol, name, exchange_code, currency_code, price,
        pre_close, open, high, low, close, change, change_ratio, volume,
        turnover, turnover_rate, market_value, amplitude.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.list_gainers_losers(
                rank_type=rank_type,
                category=category,
                sort_by=sort_by,
                direction=direction,
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
    Returns: instrument_id, symbol, name, exchange_code, currency_code, price,
        pre_close, open, high, low, close, change, change_ratio, volume,
        turnover, turnover_rate, market_value, amplitude, relative_volume_10d.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.list_most_active(
                category=category,
                rank_type=rank_type,
                sort_by=sort_by,
                direction=direction,
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
    direction: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Get all sector overview data.

    :param category: Security category, e.g. US_STOCK.
    :param agg_type: Statistics type. Default MARKET_VALUE. Enum: MARKET_VALUE, VOLUME.
    :param period: Statistics period. Default D1. Enum: D1, D5, M01, M03.
    :param direction: Sort direction: ASC or DESC.
    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: sector overview list.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.list_market_sectors(
                category=category,
                agg_type=agg_type,
                period=period,
                direction=direction,
                pagination_key=pagination_key,
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
    sort_by: Optional[str] = None,
    direction: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Get stock list and statistics for a specific sector.

    :param sector_id: Sector ID. Required.
    :param category: Security category, e.g. US_STOCK.
    :param period: Statistics period. Default D1. Enum: D1, D5, M01, M03.
    :param sort_by: Sort field. Default CHANGE_RATIO.
    :param direction: Sort direction: ASC or DESC.
    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: sector detail with stock list.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.list_market_sectors_detail(
                sector_id=sector_id,
                category=category,
                period=period,
                sort_by=sort_by,
                direction=direction,
                pagination_key=pagination_key,
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
    direction: Optional[str] = None,
) -> str:
    """Get high dividend rank list.

    :param category: Security category, e.g. US_STOCK.
    :param sort_by: Sort field. Default YIELD.
    :param direction: Sort direction: ASC or DESC.
    Returns: high dividend stocks.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.list_high_dividend(
                category=category,
                sort_by=sort_by,
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
    direction: Optional[str] = None,
) -> str:
    """Get 52-week high/low rank list.

    :param category: Security category, e.g. US_STOCK.
    :param rank_type: Index code. Enum: NEW_HIGH, NEAR_HIGH, NEW_LOW, NEAR_LOW.
    :param sort_by: Sort field. Default CHANGE_RATIO_52W.
    :param direction: Sort direction: ASC or DESC.
    Returns: 52-week high/low stocks.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.list_52whl(
                category=category,
                rank_type=rank_type,
                sort_by=sort_by,
                direction=direction,
            )
        )
        return prepend_disclaimer(format_52whl(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_52whl", config.region_id)


def get_market_sentiment(
    sdk: "SDKClient",
    config: "SkillConfig",
) -> str:
    """Query the market fear & greed sentiment index.

    Includes current index with historical comparison points
    (previous day, one week ago, one month ago).

    Returns: current, previous_day, one_week_ago, one_month_ago, time_zone.
    """
    try:
        data = extract_response_data(
            sdk.data.screener.get_fear_and_greed_index(category="US_STOCK")
        )
        return prepend_disclaimer(format_market_sentiment(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_market_sentiment", config.region_id)


def get_stock_unusual_activities(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: Optional[str] = None,
    count: int = 10,
    alert_types: Optional[str] = None,
    extended_hours_required: bool = False,
) -> str:
    """Query recent unusual activity alerts for a stock.

    US market only. Returns up to count most recent events within the last
    90 calendar days.

    :param symbol: Stock symbol, e.g. NVDA, optional (all symbols if omitted).
    :param count: Number of most recent events, 1-30, default 10.
    :param alert_types: Comma-separated alert type filter, None to return all.
    :param extended_hours_required: Whether to include pre-market and
        after-hours alerts.
    Returns: alert events with symbol, time, alert contents.
    """
    if count < 1 or count > 30:
        return "Parameter error: count must be between 1 and 30"
    try:
        data = extract_response_data(
            sdk.data.screener.get_stock_unusual_activities(
                symbol=symbol or None,
                category="US_STOCK",
                count=count,
                alert_types=alert_types or None,
                extended_hours_required=extended_hours_required,
            )
        )
        return prepend_disclaimer(format_stock_unusual_activities(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_stock_unusual_activities", config.region_id)
