"""Instrument query tools for Webull OpenAPI Skill.

Provides: get_instruments, get_futures_instruments, get_futures_instruments_by_code,
          get_futures_products, get_crypto_instruments, get_event_series,
          get_event_instruments, get_event_categories, get_event_events.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_event_categories,
    format_event_events,
    format_event_series,
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
) -> str:
    """Get stock/ETF instrument info.

    Returns: symbol, name, instrument_type, exchange.
    """
    try:
        kwargs = _build_kwargs(
            {"symbols": _split_symbols(symbols), "category": category},
            status=status,
        )
        data = extract_response_data(sdk.data.instrument.get_instrument(**kwargs))
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_instruments")


def get_futures_instruments(
    sdk: "SDKClient",
    symbols: str,
    category: str = "US_FUTURES",
) -> str:
    """Get futures instrument info.

    Returns: symbol, name, instrument_type, exchange.
    """
    try:
        sym_list = _split_symbols(symbols)
        data = extract_response_data(
            sdk.data.instrument.get_futures_instrument(symbols=sym_list, category=category)
        )
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_instruments")


def get_futures_instruments_by_code(
    sdk: "SDKClient",
    code: str,
    category: str = "US_FUTURES",
    contract_type: Optional[str] = None,
) -> str:
    """Get tradable futures contracts by product code (e.g. ES, NQ, CL).

    Returns: symbol, name, instrument_type, exchange.
    """
    try:
        kwargs = _build_kwargs(
            {"code": code, "category": category},
            contract_type=contract_type,
        )
        data = extract_response_data(sdk.data.instrument.get_futures_instrument_by_code(**kwargs))
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_instruments_by_code")


def get_futures_products(
    sdk: "SDKClient",
    category: str = "US_FUTURES",
) -> str:
    """Get all futures products and product codes.

    Returns: product_code, name, exchange.
    """
    try:
        data = extract_response_data(sdk.data.instrument.get_futures_products(category=category))
        return prepend_disclaimer(format_futures_products(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_futures_products")


def get_crypto_instruments(
    sdk: "SDKClient",
    symbols: Optional[str] = None,
    category: str = "US_CRYPTO",
    status: Optional[str] = None,
) -> str:
    """Get cryptocurrency instrument info. Returns all if symbols omitted.

    Returns: symbol, name, instrument_type, exchange.
    """
    try:
        kwargs = _build_kwargs(
            {"category": category},
            symbols=_split_symbols(symbols) if symbols else None,
            status=status,
        )
        data = extract_response_data(sdk.data.instrument.get_crypto_instrument(**kwargs))
        return prepend_disclaimer(format_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_crypto_instruments")


def get_event_series(
    sdk: "SDKClient",
    symbols: Optional[str] = None,
    category: Optional[str] = None,
    page_size: int = 500,
) -> str:
    """Get event contract series (recurring event templates).

    Returns: series_id, name, category.
    """
    try:
        kwargs = _build_kwargs(
            {},
            category=category,
            symbols=_split_symbols(symbols) if symbols else None,
            page_size=page_size if page_size != 500 else None,
        )
        data = extract_response_data(sdk.data.instrument.get_event_series(**kwargs))
        return prepend_disclaimer(format_event_series(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_event_series")


def get_event_instruments(
    sdk: "SDKClient",
    series_symbol: str,
    event_symbol: Optional[str] = None,
    symbols: Optional[str] = None,
    expiration_date_after: Optional[str] = None,
    page_size: int = 500,
) -> str:
    """Get event contract instruments by series.

    Returns: symbol, name, instrument_type, exchange.
    """
    try:
        kwargs = _build_kwargs(
            {"series_symbol": series_symbol},
            event_symbol=event_symbol,
            symbols=_split_symbols(symbols) if symbols else None,
            expiration_date_after=expiration_date_after,
            page_size=page_size if page_size != 500 else None,
        )
        data = extract_response_data(sdk.data.instrument.get_event_instrument(**kwargs))
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
