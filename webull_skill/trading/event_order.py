"""Event contract order tools for Webull OpenAPI Skill.

Provides: place_event_order, replace_event_order.

Note: Uses order_v3 SDK API (OrderOperationV3).
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from webull_skill.errors import ValidationError, handle_sdk_exception
from webull_skill.formatters import prepend_disclaimer, extract_response_data
from webull_skill.guards import validate_client_order_id
from webull_skill.trading.account import normalize_account_id, resolve_account_id

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


def _generate_client_order_id() -> str:
    """Generate a unique client order ID if not provided."""
    return str(uuid.uuid4()).replace("-", "")[:32]


def _format_order_result(data: dict) -> str:
    """Format order result to standard format."""
    result = {}
    if "client_order_id" in data:
        result["client_order_id"] = data["client_order_id"]
    if "order_id" in data:
        result["order_id"] = data["order_id"]
    if not result:
        return str(data)
    lines = [f"{k}: {v}" for k, v in result.items()]
    return "\n".join(lines)


def _build_event_order(
    symbol: str,
    side: str,
    order_type: str,
    time_in_force: str,
    quantity: float,
    limit_price: float,
    coid: str,
    event_outcome: str,
) -> dict:
    """Build the event contract order dict for the SDK."""
    order: dict = {
        "combo_type": "NORMAL",
        "instrument_type": "EVENT",
        "market": "US",
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "time_in_force": time_in_force,
        "quantity": str(quantity),
        "limit_price": str(limit_price),
        "entrust_type": "QTY",
        "client_order_id": coid,
        "event_outcome": event_outcome,
    }
    return order


# ---------------------------------------------------------------------------
# Event contract order functions
# ---------------------------------------------------------------------------

def place_event_order(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    side: str,
    quantity: float,
    limit_price: float,
    event_outcome: str,
    account_id: Optional[str] = None,
    client_order_id: Optional[str] = None,
    order_type: str = "LIMIT",
    time_in_force: str = "DAY",
) -> str:
    """Place an event contract order. LIMIT/DAY only.

    Account: Events Cash account. Call get_account_list first.
    event_outcome: Event outcome decision, possible values: yes, no.
    Returns: {client_order_id, order_id}
    """
    try:
        account_id = resolve_account_id(sdk, "event", account_id)
    except ValueError as e:
        return f"Account error: {e}"

    try:
        validate_client_order_id(client_order_id)
    except ValidationError as e:
        return f"Validation error: {e.message}"

    coid = client_order_id or _generate_client_order_id()

    order = _build_event_order(
        symbol=symbol, side=side, order_type=order_type,
        time_in_force=time_in_force, quantity=quantity,
        limit_price=limit_price, coid=coid, event_outcome=event_outcome,
    )

    try:
        response = sdk.trade.order_v3.place_order(
            account_id=account_id, new_orders=[order],
        )
        data = extract_response_data(response)
        return prepend_disclaimer(_format_order_result(data if isinstance(data, dict) else {}))
    except Exception as e:
        return handle_sdk_exception(e, "place_event_order")


def replace_event_order(
    sdk: "SDKClient",
    account_id: str,
    client_order_id: str,
    quantity: Optional[float] = None,
    limit_price: Optional[float] = None,
) -> str:
    """Modify an existing event contract order.

    Returns: {client_order_id, order_id}
    """
    try:
        validate_client_order_id(client_order_id)
    except ValidationError as e:
        return f"Validation error: {e.message}"

    account_id = normalize_account_id(account_id) or ""
    modify_order: dict = {"client_order_id": client_order_id}
    if quantity is not None:
        modify_order["quantity"] = str(quantity)
    if limit_price is not None:
        modify_order["limit_price"] = str(limit_price)

    try:
        response = sdk.trade.order_v3.replace_order(
            account_id=account_id, modify_orders=[modify_order],
        )
        data = extract_response_data(response)
        return prepend_disclaimer(_format_order_result(data if isinstance(data, dict) else {}))
    except Exception as e:
        return handle_sdk_exception(e, "replace_event_order")
