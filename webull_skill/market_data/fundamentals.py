"""Fundamentals data tools for Webull OpenAPI Skill.

Provides: get_capital_flow, get_industry_comparison, get_sec_filings,
          get_earnings_calendar, get_dividend_calendar,
          get_financials_indicators, get_financials_income,
          get_financials_cashflow, get_financials_balance_sheet,
          get_financials_alert, get_forecast_eps,
          get_fund_brief, get_fund_allocation, get_fund_holdings,
          get_fund_performance, get_fund_rating, get_fund_net_value,
          get_fund_dividends, get_fund_splits, get_fund_files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_capital_flow,
    format_industry_comparison,
    format_sec_filings,
    format_earnings_calendar,
    format_dividend_calendar,
    format_financials_indicators,
    format_financials_income,
    format_financials_cashflow,
    format_financials_balance_sheet,
    format_financials_alert,
    format_forecast_eps,
    format_fund_brief,
    format_fund_allocation,
    format_fund_holdings,
    format_fund_performance,
    format_fund_rating,
    format_fund_net_value,
    format_fund_dividends,
    format_fund_splits,
    format_fund_files,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


def get_capital_flow(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    count: Optional[int] = None,
) -> str:
    """Query the capital flow distribution for a stock.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Supported: US_STOCK, HK_STOCK, CN_STOCK, JP_STOCK.
    :param count: Number of distribution records (default 5), range 1-5.
    Returns: capital flow distribution data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_capital_flow(
                symbol=symbol, category=category, count=count,
            )
        )
        return prepend_disclaimer(format_capital_flow(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_capital_flow", config.region_id)


def get_industry_comparison(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    sort_by: Optional[str] = None,
) -> str:
    """Query industry comparison data for a stock.

    Shows up to 20 stocks in the same industry, including the target stock.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Supported: US_STOCK, HK_STOCK, CN_STOCK.
    :param sort_by: Sort field. Default: EPS_TTM. Options: EPS_TTM, NAPS, DPS_TTM,
        ROE, DEBT_TO_ASSETS, NET_MARGIN, DIV_YIELD_TTM, PE_TTM, PB_RATIO.
    Returns: industry comparison data for up to 20 peers.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_industry_comparison(
                symbol=symbol, category=category, sort_by=sort_by,
            )
        )
        return prepend_disclaimer(format_industry_comparison(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_industry_comparison", config.region_id)


def get_sec_filings(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query SEC filings for a stock. US stocks only. Returns data within last 3 years.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Only supports US_STOCK.
    Returns: SEC filing records.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_sec_filings(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_sec_filings(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_sec_filings", config.region_id)


def get_earnings_calendar(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query earnings calendar for a stock.

    Returns earnings reports within half a year before and after the current date.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Supported: US_STOCK, HK_STOCK, CN_STOCK, JP_STOCK.
    Returns: earnings calendar data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_earnings_calendar(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_earnings_calendar(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_earnings_calendar", config.region_id)


def get_dividend_calendar(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query dividend calendar for a stock.

    Returns dividends within half a year before and after the current date.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Supported: US_STOCK, HK_STOCK, CN_STOCK, JP_STOCK.
    Returns: dividend calendar data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_dividend_calendar(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_dividend_calendar(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_dividend_calendar", config.region_id)


def get_financials_indicators(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    financial_type: Optional[str] = None,
    count: Optional[int] = None,
) -> str:
    """Query financials indicators for a stock.

    :param symbol: Security symbol, e.g. TSLA.
    :param category: Security type.
    :param financial_type: ANNUAL or QUARTERLY (default QUARTERLY).
    :param count: Number of records, default 5, max 20.
    Returns: financial indicator data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_financials_indicators(
                symbol=symbol, category=category, type=financial_type, count=count,
            )
        )
        return prepend_disclaimer(format_financials_indicators(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_financials_indicators", config.region_id)


def get_financials_income(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    financial_type: Optional[str] = None,
    count: Optional[int] = None,
) -> str:
    """Query financials income statement for a stock.

    :param symbol: Security symbol, e.g. TSLA.
    :param category: Security type.
    :param financial_type: ANNUAL or QUARTERLY (default QUARTERLY).
    :param count: Number of records, default 5, max 20.
    Returns: income statement data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_financials_income(
                symbol=symbol, category=category, type=financial_type, count=count,
            )
        )
        return prepend_disclaimer(format_financials_income(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_financials_income", config.region_id)


def get_financials_cashflow(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    financial_type: Optional[str] = None,
    count: Optional[int] = None,
) -> str:
    """Query financials cashflow statement for a stock.

    :param symbol: Security symbol, e.g. TSLA.
    :param category: Security type.
    :param financial_type: ANNUAL or QUARTERLY (default QUARTERLY).
    :param count: Number of records, default 5, max 20.
    Returns: cashflow statement data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_financials_cashflow(
                symbol=symbol, category=category, type=financial_type, count=count,
            )
        )
        return prepend_disclaimer(format_financials_cashflow(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_financials_cashflow", config.region_id)


def get_financials_balance_sheet(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    financial_type: Optional[str] = None,
    count: Optional[int] = None,
) -> str:
    """Query financials balance sheet for a stock.

    :param symbol: Security symbol, e.g. TSLA.
    :param category: Security type.
    :param financial_type: ANNUAL or QUARTERLY (default QUARTERLY).
    :param count: Number of records, default 5, max 20.
    Returns: balance sheet data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_financials_balance_sheet(
                symbol=symbol, category=category, type=financial_type, count=count,
            )
        )
        return prepend_disclaimer(format_financials_balance_sheet(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_financials_balance_sheet", config.region_id)


def get_financials_alert(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query financials alert for a stock.

    :param symbol: Security symbol, e.g. TSLA.
    :param category: Security type.
    Returns: financial alert data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_financials_alert(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_financials_alert(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_financials_alert", config.region_id)


def get_forecast_eps(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query forecast EPS for a stock.

    Returns the historical actual EPS of the most recent four disclosed fiscal periods,
    plus the latest analyst consensus forecast EPS (if available). Up to 5 records,
    sorted by time ascending.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Supported: US_STOCK, HK_STOCK, CN_STOCK.
    Returns: forecast EPS data with fiscal_year, fiscal_period, actual, est, reported.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_forecast_eps(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_forecast_eps(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_forecast_eps", config.region_id)


def get_fund_brief(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query fund brief information.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    Returns: fund brief data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_brief(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_fund_brief(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_brief", config.region_id)


def get_fund_allocation(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query fund asset allocation.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    Returns: fund allocation data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_allocation(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_fund_allocation(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_allocation", config.region_id)


def get_fund_holdings(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query fund top 10 holdings.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    Returns: fund top holdings data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_holdings(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_fund_holdings(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_holdings", config.region_id)


def get_fund_performance(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query fund performance.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    Returns: fund performance data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_performance(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_fund_performance(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_performance", config.region_id)


def get_fund_rating(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query fund rating.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    Returns: fund rating data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_rating(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_fund_rating(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_rating", config.region_id)


def get_fund_net_value(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    last_date: Optional[str] = None,
    count: Optional[int] = None,
) -> str:
    """Query fund net value.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    :param last_date: Last query date, e.g. 2026-04-01.
    :param count: Number of records, default 5, max 20.
    Returns: fund net value data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_net_value(
                symbol=symbol, category=category, last_date=last_date, count=count,
            )
        )
        return prepend_disclaimer(format_fund_net_value(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_net_value", config.region_id)


def get_fund_dividends(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
    page_index: Optional[int] = None,
    page_size: Optional[int] = None,
) -> str:
    """Query fund dividends.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    :param page_index: Page index, default 1.
    :param page_size: Records per page, default 10, max 20.
    Returns: fund dividend data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_dividends(
                symbol=symbol, category=category,
                page_index=page_index, page_size=page_size,
            )
        )
        return prepend_disclaimer(format_fund_dividends(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_dividends", config.region_id)


def get_fund_splits(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query fund splits.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    Returns: fund split data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_splits(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_fund_splits(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_splits", config.region_id)


def get_fund_files(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Query fund files.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    Returns: fund file data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_fund_files(
                symbol=symbol, category=category,
            )
        )
        return prepend_disclaimer(format_fund_files(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_fund_files", config.region_id)
