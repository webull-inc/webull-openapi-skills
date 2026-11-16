"""Instrument query tools for Webull OpenAPI Skill.

Provides: get_instruments, get_futures_instruments,
          get_futures_products, get_futures_product_class,
          get_crypto_instruments, get_event_series,
          get_event_instruments, get_event_categories, get_event_events,
          get_company_profile, get_analyst_rating, get_analyst_target_price.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_analyst_rating,
    format_analyst_target_price,
    format_company_profile,
    format_event_categories,
    format_event_events,
    format_event_series,
    format_futures_product_classes,
    format_futures_products,
    format_instruments,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.sdk_client import SDKClient


def _build_kwargs(base: dict[str, Any], **optional: Any) -> dict[str, Any]:
    """Build kwargs dict, adding only non-None optional values."""
    for key, value in optional.items():
        if value is not None:
            base[key] = value
    return base


def _split_symbols(symbols: str) -> list[str]:
    """Split a comma-separated symbols string into a list."""
    return [s.strip() for s in symbols.split(",") if s.strip()]


def get_instruments(
    sdk: "SDKClient",
    symbols: str,
    category: str = "US_STOCK",
    status: Optional[str] = None,
    sub_category: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Get stock/ETF instrument info.

    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: symbol, name, instrument_type, exchange, sub_category.
    """
    try:
        kwargs = _build_kwargs(
            {"symbols": _split_symbols(symbols), "category": category},
            status=status,
            sub_category=sub_category,
            pagination_key=pagination_key,
        )
        data = extract_response_data(sdk.data.instrument.list_instruments(**kwargs))
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_instruments")


def get_futures_instruments(
    sdk: "SDKClient",
    symbols: str = "",
    category: str = "US_FUTURES",
    code: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """Get futures instrument info.

    Two ways to query: by contract symbols (e.g. ESM6) or by product code (e.g. ES).
    At least one of symbols or code is required.
    status: OC (Tradable), CO (Liquidate only), NT (Non-Tradable). Server default is OC.
    Returns: symbol, name, instrument_type, exchange.
    """
    if not symbols and not code:
        return "Validation error: provide --symbols (contract symbols, e.g. ESM6) or --code (product code, e.g. ES)"
    try:
        kwargs = _build_kwargs(
            {"category": category},
            symbols=_split_symbols(symbols) if symbols else None,
            code=code,
            status=status,
        )
        data = extract_response_data(
            sdk.data.instrument.get_futures_instrument(**kwargs)
        )
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_instruments")


def get_futures_products(
    sdk: "SDKClient",
    category: str = "US_FUTURES",
    product_class_id: Optional[str] = None,
) -> str:
    """Get futures products and product codes.

    :param product_class_id: Product class ID (from get_futures_product_class)
        used to filter products; omit to list all products.
    Returns: product_code, name, exchange.
    """
    try:
        kwargs = _build_kwargs({"category": category}, product_class_id=product_class_id)
        data = extract_response_data(sdk.data.instrument.get_futures_products(**kwargs))
        return prepend_disclaimer(format_futures_products(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_products")


def get_futures_product_class(
    sdk: "SDKClient",
    category: str = "US_FUTURES",
) -> str:
    """Get all futures product classification groups.

    Returns: class_id, name, product codes in each class.
    """
    try:
        data = extract_response_data(sdk.data.instrument.get_futures_product_class(category=category))
        return prepend_disclaimer(format_futures_product_classes(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_product_class")


def get_crypto_instruments(
    sdk: "SDKClient",
    symbols: Optional[str] = None,
    category: str = "US_CRYPTO",
    status: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Get cryptocurrency instrument info. Returns all if symbols omitted.

    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: symbol, name, instrument_type, exchange.
    """
    try:
        kwargs = _build_kwargs(
            {"category": category},
            symbols=_split_symbols(symbols) if symbols else None,
            status=status,
            pagination_key=pagination_key,
        )
        data = extract_response_data(sdk.data.instrument.list_crypto_instruments(**kwargs))
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_crypto_instruments")


def get_event_series(
    sdk: "SDKClient",
    symbols: Optional[str] = None,
    category: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Get event contract series (recurring event templates).

    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: series_id, name, category.
    """
    try:
        kwargs = _build_kwargs(
            {},
            category=category,
            symbols=_split_symbols(symbols) if symbols else None,
            pagination_key=pagination_key,
        )
        data = extract_response_data(sdk.data.instrument.list_event_series(**kwargs))
        return prepend_disclaimer(format_event_series(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_series")


def get_event_instruments(
    sdk: "SDKClient",
    series_symbol: str,
    event_symbol: Optional[str] = None,
    symbols: Optional[str] = None,
    expiration_date_after: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Get event contract instruments by series.

    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: symbol, name, instrument_type, exchange.
    """
    try:
        kwargs = _build_kwargs(
            {"series_symbol": series_symbol},
            event_symbol=event_symbol,
            symbols=_split_symbols(symbols) if symbols else None,
            expiration_date_after=expiration_date_after,
            pagination_key=pagination_key,
        )
        data = extract_response_data(sdk.data.instrument.list_event_instruments(**kwargs))
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_instruments")


def get_event_categories(sdk: "SDKClient") -> str:
    """Get event contract category list.

    Returns: category_id, name.
    """
    try:
        data = extract_response_data(sdk.data.instrument.get_event_categories())
        return prepend_disclaimer(format_event_categories(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_categories")


def get_event_events(
    sdk: "SDKClient",
    series_symbol: str,
    symbols: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """Get events within a series.

    Returns: event_id, name, status, expiration_date.
    """
    try:
        kwargs = _build_kwargs(
            {"series_symbol": series_symbol},
            symbols=_split_symbols(symbols) if symbols else None,
            status=status,
        )
        data = extract_response_data(sdk.data.instrument.get_event_events(**kwargs))
        return prepend_disclaimer(format_event_events(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_events")


def get_company_profile(
    sdk: "SDKClient",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Get company profile for a stock instrument.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Currently only US_STOCK is supported.
    Returns: company name, establish date, CEO, employees, address,
             profile description, industries, sector, etc.
    """
    try:
        data = extract_response_data(
            sdk.data.instrument.get_company_profile(symbol=symbol, category=category)
        )
        return prepend_disclaimer(format_company_profile(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_company_profile")


def get_analyst_rating(
    sdk: "SDKClient",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Get analyst rating for a stock instrument.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Currently only US_STOCK is supported.
    Returns: total analysts, buy/hold/sell counts, strong buy, underperform counts.
    """
    try:
        data = extract_response_data(
            sdk.data.instrument.get_analyst_rating(symbol=symbol, category=category)
        )
        return prepend_disclaimer(format_analyst_rating(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_analyst_rating")


def get_analyst_target_price(
    sdk: "SDKClient",
    symbol: str,
    category: str = "US_STOCK",
) -> str:
    """Get analyst target price for a stock instrument.

    :param symbol: Security symbol, e.g. AAPL.
    :param category: Security type. Currently only US_STOCK is supported.
    Returns: mean, low, high, median target prices and currency.
    """
    try:
        data = extract_response_data(
            sdk.data.instrument.get_analyst_target_price(symbol=symbol, category=category)
        )
        return prepend_disclaimer(format_analyst_target_price(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_analyst_target_price")


def _option_contracts_filter_error(
    *,
    category: str,
    status: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
    option_type: Optional[str],
    style: Optional[str],
    strike_price_gte: Optional[str],
    strike_price_lte: Optional[str],
    ppind: Optional[str],
    show_deliverables: Optional[str],
) -> str:
    """Validate option contract filters against the documented values. Returns "" when valid."""
    enums = (
        ("category", category, ("US_OPTION",)),
        ("status", status, ("LISTING", "DELISTING")),
        ("option_type", option_type, ("CALL", "PUT")),
        ("style", style, ("AMERICAN", "EUROPEAN")),
        ("ppind", ppind, ("true", "false")),
        ("show_deliverables", show_deliverables, ("true", "false")),
    )
    for field, value, allowed in enums:
        if value is not None and value not in allowed:
            return f"Invalid {field} '{value}', must be one of {list(allowed)}"
    for field, value in (("start_date", start_date), ("end_date", end_date)):
        if value is not None:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return f"{field} must use YYYY-MM-DD format"
    bounds: dict[str, Decimal] = {}
    for field, value in (("strike_price_gte", strike_price_gte), ("strike_price_lte", strike_price_lte)):
        if value is None:
            continue
        try:
            number = Decimal(str(value))
        except InvalidOperation:
            return f"{field} must be a positive decimal"
        if not number.is_finite() or number <= 0:
            return f"{field} must be a positive decimal"
        bounds[field] = number
    if len(bounds) == 2 and bounds["strike_price_gte"] > bounds["strike_price_lte"]:
        return "strike_price_gte must not exceed strike_price_lte"
    return ""


def get_option_contracts(
    sdk: "SDKClient",
    underlying_symbols: Optional[str] = None,
    category: str = "US_OPTION",
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    root_symbol: Optional[str] = None,
    option_symbols: Optional[str] = None,
    option_type: Optional[str] = None,
    style: Optional[str] = None,
    strike_price_gte: Optional[str] = None,
    strike_price_lte: Optional[str] = None,
    ppind: Optional[str] = None,
    show_deliverables: Optional[str] = None,
    pagination_key: Optional[str] = None,
) -> str:
    """Query option contract list by underlying symbols, status, and other attributes.

    :param underlying_symbols: Underlying symbol(s), comma-separated. e.g. AAPL,MSFT.
    :param category: Market category. Value: US_OPTION.
    :param status: Contract status: LISTING (default), DELISTING.
    :param start_date: Expiration date exact match, format YYYY-MM-DD.
    :param end_date: Expiration date lower bound (inclusive), format YYYY-MM-DD.
    :param root_symbol: Root symbol filter (series symbol, e.g. SPXW).
    :param option_symbols: Option symbol(s), comma-separated. e.g. AAPL250620C00150000.
    :param option_type: Contract type: CALL / PUT.
    :param style: Exercise style: AMERICAN / EUROPEAN.
    :param strike_price_gte: Strike price lower bound (inclusive).
    :param strike_price_lte: Strike price upper bound (inclusive).
    :param ppind: Penny Program Indicator: true / false.
    :param show_deliverables: Return deliverables array: true / false.
    :param pagination_key: Pagination key from the previous page response;
        omit for the first page. Not returned on the last page.
    Returns: option contract static information.
    """
    error = _option_contracts_filter_error(
        category=category, status=status, start_date=start_date, end_date=end_date,
        option_type=option_type, style=style,
        strike_price_gte=strike_price_gte, strike_price_lte=strike_price_lte,
        ppind=ppind, show_deliverables=show_deliverables,
    )
    if error:
        return f"Validation error: {error}"
    try:
        kwargs = _build_kwargs(
            {"category": category},
            underlying_symbols=underlying_symbols,
            status=status,
            start_date=start_date,
            end_date=end_date,
            root_symbol=root_symbol,
            option_symbols=option_symbols,
            option_type=option_type,
            style=style,
            strike_price_gte=strike_price_gte,
            strike_price_lte=strike_price_lte,
            ppind=ppind,
            show_deliverables=show_deliverables,
            pagination_key=pagination_key,
        )
        data = extract_response_data(sdk.data.instrument.list_option_contracts(**kwargs))
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_option_contracts")
