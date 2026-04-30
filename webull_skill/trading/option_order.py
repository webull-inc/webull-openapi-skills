"""Option order tools for Webull OpenAPI Skill.

Provides: place_option_single_order, preview_option_order, replace_option_order,
          place_option_strategy_order.

Note: Uses order_v3 SDK API (OrderOperationV3).
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional

from webull_skill.errors import ValidationError, handle_sdk_exception
from webull_skill.formatters import (
    prepend_disclaimer,
    extract_response_data,
    format_order_preview,
)
from webull_skill.guards import (
    validate_client_order_id,
    validate_option_order,
    validate_option_strategy_order,
)
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
    if "client_combo_order_id" in data:
        result["client_combo_order_id"] = data["client_combo_order_id"]
    if "combo_order_id" in data:
        result["combo_order_id"] = data["combo_order_id"]
    if "order_id" in data:
        result["order_id"] = data["order_id"]
    if not result:
        return str(data)
    lines = [f"{k}: {v}" for k, v in result.items()]
    return "\n".join(lines)


def _add_optional_str(order: dict, key: str, value: Any) -> None:
    """Add a value to order dict as string if not None."""
    if value is not None:
        order[key] = str(value)


def _build_option_order(
    coid: str,
    symbol: str,
    side: str,
    quantity: int,
    option_type: str,
    strike_price: float,
    expiration_date: str,
    order_type: str,
    time_in_force: str,
    limit_price: float | None,
    stop_price: float | None,
    position_intent: str | None = None,
    sender_sub_id: str | None = None,
) -> dict:
    """Build a single-leg option order dict for the SDK."""
    order: dict = {
        "client_order_id": coid,
        "combo_type": "NORMAL",
        "order_type": order_type,
        "quantity": str(quantity),
        "option_strategy": "SINGLE",
        "side": side,
        "time_in_force": time_in_force,
        "entrust_type": "QTY",
        "legs": [
            {
                "side": side,
                "quantity": str(quantity),
                "symbol": symbol,
                "strike_price": str(strike_price),
                "option_expire_date": expiration_date,
                "instrument_type": "OPTION",
                "option_type": option_type,
                "market": "US",
            }
        ],
    }
    _add_optional_str(order, "limit_price", limit_price)
    _add_optional_str(order, "stop_price", stop_price)
    if position_intent is not None:
        order["position_intent"] = position_intent
    if sender_sub_id is not None:
        order["sender_sub_id"] = sender_sub_id
    return order


def _extract_leg_ids(detail: dict | None, quantity: int | None) -> list[dict] | None:
    """Extract leg IDs from order detail for US option replace.

    For multi-leg strategies (e.g. COVERED_STOCK), each leg's quantity is
    scaled proportionally. The quantity parameter represents the new
    top-level (option contract) quantity. Each leg is scaled by the ratio
    original_leg_qty / original_option_qty where original_option_qty
    is the top-level total_quantity from the order detail.

    Returns list of {id, quantity} dicts, or None if no legs found.
    """
    if not detail or not isinstance(detail, dict):
        return None
    orders = detail.get("orders", [])
    if not orders:
        return None
    for order in orders:
        legs = order.get("legs", [])
        if not legs:
            continue

        # Determine the original top-level quantity for ratio calculation
        orig_top_qty_str = order.get("total_quantity") or order.get("quantity")
        orig_top_qty = float(orig_top_qty_str) if orig_top_qty_str else None

        result = []
        for leg in legs:
            leg_id = leg.get("id")
            if not leg_id:
                return None
            entry: dict = {"id": leg_id}
            if quantity is not None:
                orig_leg_qty_str = leg.get("quantity") or leg.get("total_quantity")
                orig_leg_qty = float(orig_leg_qty_str) if orig_leg_qty_str else None
                if orig_top_qty and orig_leg_qty and orig_top_qty > 0:
                    ratio = orig_leg_qty / orig_top_qty
                    entry["quantity"] = str(int(quantity * ratio))
                else:
                    entry["quantity"] = str(quantity)
            result.append(entry)
        return result
    return None


def _build_strategy_order(
    coid: str,
    strategy: str,
    order_type: str,
    time_in_force: str,
    legs: list[dict],
    quantity: int | None,
    limit_price: float | None,
    symbol: str | None = None,
) -> dict:
    """Build a multi-leg option strategy order dict for the SDK.

    Structure: one order with a legs array inside, not multiple orders.
    """
    # Use explicit symbol, or fall back to first option leg
    if not symbol:
        first_option = next((l for l in legs if l.get("instrument_type", "OPTION") == "OPTION"), legs[0])
        symbol = first_option["symbol"]

    order: dict = {
        "client_order_id": coid,
        "combo_type": "NORMAL",
        "option_strategy": strategy,
        "order_type": order_type,
        "side": legs[0]["side"],
        "time_in_force": time_in_force,
        "entrust_type": "QTY",
        "instrument_type": "OPTION",
        "market": "US",
        "symbol": symbol,
    }
    if quantity is not None:
        order["quantity"] = str(quantity)
    _add_optional_str(order, "limit_price", limit_price)

    # Build legs array matching API demo payloads
    order_legs = []
    for leg in legs:
        inst_type = leg.get("instrument_type", "OPTION")
        leg_dict: dict = {
            "side": leg["side"],
            "quantity": str(leg["quantity"]),
            "symbol": leg["symbol"],
        }
        # Option-specific fields before instrument_type/market
        if inst_type == "OPTION":
            if leg.get("strike_price") is not None:
                leg_dict["strike_price"] = str(leg["strike_price"])
            expire = leg.get("option_expire_date") or leg.get("expiration_date")
            if expire:
                leg_dict["option_expire_date"] = expire
        leg_dict["instrument_type"] = inst_type
        if inst_type == "OPTION" and leg.get("option_type"):
            leg_dict["option_type"] = leg["option_type"]
        leg_dict["market"] = leg.get("market", "US")
        order_legs.append(leg_dict)

    order["legs"] = order_legs
    return order


# ---------------------------------------------------------------------------
# Single-leg option order functions
# ---------------------------------------------------------------------------

def place_option_single_order(
    sdk: "SDKClient",
    config: "SkillConfig",
    symbol: str,
    side: str,
    quantity: int,
    option_type: str,
    strike_price: float,
    expiration_date: str,
    order_type: str,
    time_in_force: str,
    account_id: Optional[str] = None,
    client_order_id: Optional[str] = None,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    position_intent: Optional[str] = None,
    sender_sub_id: Optional[str] = None,
) -> str:
    """Place a single-leg option order. For multi-leg use place_option_strategy_order.

    Account: stock/option account (Individual Cash, Individual Margin, IRA).
    Call get_account_list first.
    order_type: MARKET, LIMIT, STOP_LOSS, STOP_LOSS_LIMIT.
    time_in_force: DAY, GTC. trading_session: CORE only.
    position_intent: BUY_TO_OPEN, BUY_TO_CLOSE, SELL_TO_OPEN, SELL_TO_CLOSE (optional, US only).
    sender_sub_id: Broker user UUID (optional, HK region institutional only).
    Returns: {client_order_id, order_id}
    """
    try:
        account_id = resolve_account_id(sdk, "option", account_id)
    except ValueError as e:
        return f"Account error: {e}"

    params: dict = {"side": side, "order_type": order_type, "time_in_force": time_in_force}
    if limit_price is not None:
        params["limit_price"] = limit_price
    if stop_price is not None:
        params["stop_price"] = stop_price
    try:
        validate_option_order(params, config)
    except ValidationError as e:
        return f"Validation error: {e.message}"

    try:
        validate_client_order_id(client_order_id)
    except ValidationError as e:
        return f"Validation error: {e.message}"

    coid = client_order_id or _generate_client_order_id()

    order = _build_option_order(
        coid=coid, symbol=symbol, side=side, quantity=quantity,
        option_type=option_type, strike_price=strike_price,
        expiration_date=expiration_date, order_type=order_type,
        time_in_force=time_in_force,
        limit_price=limit_price, stop_price=stop_price,
        position_intent=position_intent,
        sender_sub_id=sender_sub_id,
    )

    try:
        response = sdk.trade.order_v3.place_order(
            account_id=account_id, new_orders=[order],
        )
        data = extract_response_data(response)
        return prepend_disclaimer(_format_order_result(data if isinstance(data, dict) else {}))
    except Exception as e:
        return handle_sdk_exception(e, "place_option_single_order")


def preview_option_order(
    sdk: "SDKClient",
    config: "SkillConfig",
    account_id: str,
    symbol: str,
    side: str,
    quantity: int,
    option_type: str,
    strike_price: float,
    expiration_date: str,
    order_type: str,
    time_in_force: str,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> str:
    """Preview an option order without submitting. Returns: estimated cost and fees."""
    account_id = normalize_account_id(account_id) or ""
    preview_order = _build_option_order(
        coid=_generate_client_order_id(),
        symbol=symbol, side=side, quantity=quantity,
        option_type=option_type, strike_price=strike_price,
        expiration_date=expiration_date, order_type=order_type,
        time_in_force=time_in_force,
        limit_price=limit_price, stop_price=stop_price,
    )

    try:
        response = sdk.trade.order_v3.preview_order(
            account_id=account_id, preview_orders=[preview_order],
        )
        data = extract_response_data(response)
        return prepend_disclaimer(format_order_preview(data if isinstance(data, dict) else {}))
    except Exception as e:
        return handle_sdk_exception(e, "preview_option_order")


def replace_option_order(
    sdk: "SDKClient",
    account_id: str,
    client_order_id: str,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
    quantity: Optional[int] = None,
    time_in_force: Optional[str] = None,
) -> str:
    """Modify an existing option order. Auto-fetches leg IDs for US region.

    Returns: {client_order_id, order_id}
    """
    try:
        validate_client_order_id(client_order_id)
    except ValidationError as e:
        return f"Validation error: {e.message}"

    account_id = normalize_account_id(account_id) or ""
    modify_order: dict = {"client_order_id": client_order_id}
    _add_optional_str(modify_order, "limit_price", limit_price)
    _add_optional_str(modify_order, "stop_price", stop_price)
    if quantity is not None:
        modify_order["quantity"] = str(quantity)
    if time_in_force is not None:
        modify_order["time_in_force"] = time_in_force

    # US option replace requires legs with id and quantity
    # Auto-fetch leg IDs from order detail
    try:
        detail_resp = sdk.trade.order_v3.get_order_detail(
            account_id=account_id, client_order_id=client_order_id,
        )
        detail = extract_response_data(detail_resp)
        legs = _extract_leg_ids(detail, quantity)
        if legs:
            modify_order["legs"] = legs
    except Exception:
        pass  # If detail fetch fails, try without legs

    try:
        response = sdk.trade.order_v3.replace_order(
            account_id=account_id, modify_orders=[modify_order],
        )
        data = extract_response_data(response)
        return prepend_disclaimer(_format_order_result(data if isinstance(data, dict) else {}))
    except Exception as e:
        return handle_sdk_exception(e, "replace_option_order")


# ---------------------------------------------------------------------------
# Multi-leg option strategy order functions
# ---------------------------------------------------------------------------

def place_option_strategy_order(
    sdk: "SDKClient",
    config: "SkillConfig",
    account_id: str,
    strategy: str,
    symbol: str,
    order_type: str,
    time_in_force: str,
    legs: list[dict],
    quantity: Optional[int] = None,
    client_order_id: Optional[str] = None,
    limit_price: Optional[float] = None,
) -> str:
    """Place a multi-leg option strategy order (US only).

    Strategies: VERTICAL, STRADDLE, STRANGLE, BUTTERFLY, CONDOR, etc.
    Returns: {client_order_id, combo_order_id, order_id}
    """
    account_id = normalize_account_id(account_id) or ""
    params: dict = {
        "strategy": strategy, "order_type": order_type,
        "time_in_force": time_in_force, "legs": legs,
    }
    try:
        validate_option_strategy_order(params, config)
    except ValidationError as e:
        return f"Validation error: {e.message}"

    try:
        validate_client_order_id(client_order_id)
    except ValidationError as e:
        return f"Validation error: {e.message}"

    coid = client_order_id or _generate_client_order_id()

    order = _build_strategy_order(
        coid=coid, strategy=strategy, order_type=order_type,
        time_in_force=time_in_force, legs=legs,
        quantity=quantity, limit_price=limit_price,
        symbol=symbol,
    )

    try:
        response = sdk.trade.order_v3.place_order(
            account_id=account_id, new_orders=[order],
        )
        data = extract_response_data(response)
        return prepend_disclaimer(_format_order_result(data if isinstance(data, dict) else {}))
    except Exception as e:
        return handle_sdk_exception(e, "place_option_strategy_order")
