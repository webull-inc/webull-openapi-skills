"""Fundamentals data tools for Webull OpenAPI Skill.

Provides: get_capital_flow, get_industry_comparison, get_sec_filings,
          get_earnings_calendar, get_dividend_calendar,
          get_financials_indicators, get_financials_income,
          get_financials_cashflow, get_financials_balance_sheet,
          get_financials_alert, get_forecast_eps,
          get_fund_brief, get_fund_allocation, get_fund_holdings,
          get_fund_performance, get_fund_rating, get_fund_net_value,
          get_fund_dividends, get_fund_splits, get_fund_files,
          search_institutions, get_institution_holdings,
          get_institution_holding_changes, get_insider_transactions,
          get_insider_holdings_overview, get_economic_calendar (US only).
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
    format_institution_search,
    format_institution_holdings,
    format_institution_holding_changes,
    format_insider_transactions,
    format_insider_holdings_overview,
    format_economic_calendar,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


VALID_HOLDING_CHANGE_POSITIONS = frozenset({"OPEN", "CLOSE", "CHANGE"})
VALID_INSIDER_TRANSACTION_SIDES = frozenset({"BUY", "SELL"})


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
    pagination_key: Optional[str] = None,
) -> str:
    """Query fund dividends.

    :param symbol: Security symbol, e.g. QQQ.
    :param category: Security type.
    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: fund dividend data.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.list_fund_dividends(
                symbol=symbol, category=category,
                pagination_key=pagination_key,
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


def search_institutions(
    sdk: "SDKClient",
    config: "SkillConfig",
    keyword: str,
    pagination_key: Optional[str] = None,
) -> str:
    """Search US institutional investors by name or SEC CIK number.

    US market only.

    :param keyword: Search keyword (institution name or CIK), required.
    :param pagination_key: Pagination key from the previous page response;
        not returned on the last page.
    Returns: institution list with cik, name, notable_people.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_institution_search(keyword, pagination_key)
        )
        return prepend_disclaimer(format_institution_search(data))
    except Exception as e:
        return handle_sdk_exception(e, "search_institutions", config.region_id)


def get_institution_holdings(
    sdk: "SDKClient",
    config: "SkillConfig",
    cik: str,
    pagination_key: Optional[str] = None,
) -> str:
    """Query a US institution's 13F holdings. US market only.

    :param cik: Institution CIK number, required.
    :param pagination_key: Pagination key from the previous page response;
        not returned on the last page.
    Returns: 13F holdings list.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_institution_holdings(cik, pagination_key)
        )
        return prepend_disclaimer(format_institution_holdings(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_institution_holdings", config.region_id)


def get_institution_holding_changes(
    sdk: "SDKClient",
    config: "SkillConfig",
    cik: str,
    position: str,
    pagination_key: Optional[str] = None,
) -> str:
    """Query US institutional holding changes filtered by position type.

    US market only.

    :param cik: Fund CIK number, required.
    :param position: Position type: OPEN, CLOSE, or CHANGE, required.
    :param pagination_key: Pagination key from the previous page response;
        not returned on the last page.
    Returns: holding change records.
    """
    if not isinstance(position, str):
        return "Parameter error: position must be one of OPEN, CLOSE, CHANGE"
    position = position.strip().upper()
    if position not in VALID_HOLDING_CHANGE_POSITIONS:
        return "Parameter error: position must be one of OPEN, CLOSE, CHANGE"
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_institution_holding_changes(
                cik, position, pagination_key=pagination_key,
            )
        )
        return prepend_disclaimer(format_institution_holding_changes(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_institution_holding_changes", config.region_id)


def get_insider_transactions(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    side: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Query insider transaction records for a stock.

    US market only.

    :param symbol: Stock symbol, e.g. NVDA, required.
    :param side: Transaction side filter: BUY or SELL, None to return all.
    :param pagination_key: Pagination key from the previous page response;
        not returned on the last page.
    Returns: insider transactions with side, shares, price, insider_name,
        transaction_date, shares_after.
    """
    if side is not None:
        if not isinstance(side, str):
            return "Parameter error: side must be BUY or SELL"
        side = side.strip().upper() or None
        if side is not None and side not in VALID_INSIDER_TRANSACTION_SIDES:
            return "Parameter error: side must be BUY or SELL"
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_insider_transactions(
                symbol,
                category="US_STOCK",
                side=side,
                pagination_key=pagination_key,
            )
        )
        return prepend_disclaimer(format_insider_transactions(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_insider_transactions", config.region_id)


def get_insider_holdings_overview(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    compare_months: int = 1,
) -> str:
    """Query the insider ownership statistics overview for a stock.

    US market only.

    :param symbol: Stock symbol, e.g. NVDA, required.
    :param compare_months: Comparison period in months: 1 (default) or 3.
    Returns: insiders_count, total_shares_held, ownership_pct and changes.
    """
    if type(compare_months) is not int or compare_months not in (1, 3):
        return "Parameter error: compare_months must be 1 or 3"
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_insider_holdings(
                symbol, category="US_STOCK", compare_months=compare_months,
            )
        )
        return prepend_disclaimer(format_insider_holdings_overview(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_insider_holdings_overview", config.region_id)


def get_economic_calendar(
    sdk: "SDKClient",
    config: "SkillConfig",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Query the US macroeconomic event calendar.

    US market only. Results are cursor-paginated, up to 30 events per page.

    :param start_date: Start date in yyyy-MM-dd format, None defaults to today.
    :param end_date: End date in yyyy-MM-dd format, None defaults to
        start date + 7 days.
    :param pagination_key: Pagination key from the previous page response;
        not returned on the last page.
    Returns: economic events with event_name, publish_date, period,
        unit, frequency, prior_value, is_fed_related.
    """
    try:
        data = extract_response_data(
            sdk.data.fundamentals.get_economic_calendars(
                region="US",
                start_date=start_date,
                end_date=end_date,
                pagination_key=pagination_key,
            )
        )
        return prepend_disclaimer(format_economic_calendar(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_economic_calendar", config.region_id)
