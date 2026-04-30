"""Universal order tools for Webull OpenAPI Skill.

Provides: cancel_order, get_order_history, get_open_orders, get_order_detail.

Note: preview_order, place_order, replace_order have been replaced by
fine-grained tools in stock_order.py, option_order.py, futures_order.py,
crypto_order.py, and event_order.py.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    prepend_disclaimer,
    extract_response_data,
    format_open_orders,
    format_order_detail,
    format_order_history,
)
from webull_skill.guards import validate_client_order_id
from webull_skill.trading.account import normalize_account_id

if TYPE_CHECKING:
    from webull_skill.sdk_client import SDKClient


def _format_cancel_result(data: dict) -> str:
    """Format cancel order result to standard format."""
    result = {}
    if "client_order_id" in data:
        result["client_order_id"] = data["client_order_id"]
    if "client_combo_order_id" in data:
        result["client_combo_order_id"] = data["client_combo_order_id"]
    if "combo_order_id" in data:
        result["combo_order_id"] = data["combo_order_id"]
    if "order_id" in data:
        result["order_id"] = data["order_id"]

    if not result:
        return f"Order cancelled: {data}"

    lines = [f"{k}: {v}" for k, v in result.items()]
    return "Order cancelled:\n" + "\n".join(lines)


def cancel_order(
    sdk: "SDKClient",
    account_id: str,
    client_order_id: str,
) -> str:
    """Cancel an unfilled order. Works for stocks, options, futures, crypto, event contracts.

    Returns: {client_order_id, order_id}
    """
    try:
        validate_client_order_id(client_order_id)
    except Exception as e:
        return f"Validation error: {e}"

    account_id = normalize_account_id(account_id) or ""
    try:
        response = sdk.trade.order_v3.cancel_order(
            account_id=account_id, client_order_id=client_order_id
        )
        data = extract_response_data(response)
        if isinstance(data, dict):
            return prepend_disclaimer(_format_cancel_result(data))
        return prepend_disclaimer(f"Order {client_order_id} cancelled successfully.")
    except Exception as e:
        return handle_sdk_exception(e, "cancel_order")


# ---------------------------------------------------------------------------
# Order query functions
# ---------------------------------------------------------------------------

def get_order_history(
    sdk: "SDKClient",
    account_id: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    limit: Optional[int] = 10,
) -> str:
    """Get historical orders, default last 7 days.

    Returns: client_order_id, symbol, side, order_type, quantity,
    filled_quantity, price, avg_filled_price, status,
    time_in_force, create_time.
    """
    account_id = normalize_account_id(account_id) or ""
    try:
        kwargs: dict = {}
        if start:
            kwargs["start_date"] = start
        if end:
            kwargs["end_date"] = end
        if limit:
            kwargs["page_size"] = limit
        response = sdk.trade.order_v3.get_order_history(account_id=account_id, **kwargs)
        data = extract_response_data(response)
        return prepend_disclaimer(format_order_history(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_order_history")


def get_open_orders(
    sdk: "SDKClient",
    account_id: str,
    limit: Optional[int] = 10,
) -> str:
    """Get all current open/pending orders. Returns same fields as get_order_history."""
    account_id = normalize_account_id(account_id) or ""
    try:
        kwargs: dict = {}
        if limit:
            kwargs["page_size"] = limit
        response = sdk.trade.order_v3.get_order_open(account_id=account_id, **kwargs)
        data = extract_response_data(response)
        return prepend_disclaimer(format_open_orders(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_open_orders")


def get_order_detail(
    sdk: "SDKClient",
    account_id: str,
    client_order_id: str,
) -> str:
    """Get single order details.

    Returns: client_order_id, symbol, side, order_type, quantity,
    filled_quantity, price, avg_filled_price, status, time_in_force,
    trading_session, create_time, update_time.
    """
    account_id = normalize_account_id(account_id) or ""
    try:
        response = sdk.trade.order_v3.get_order_detail(
            account_id=account_id, client_order_id=client_order_id
        )
        data = extract_response_data(response)
        return prepend_disclaimer(format_order_detail(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_order_detail")
