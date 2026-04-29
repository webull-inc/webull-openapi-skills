"""Assets tools for Webull OpenAPI Skill.

Provides: get_account_balance, get_account_positions, get_account_position_details.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_account_balance,
    format_position_details,
    format_positions,
    prepend_disclaimer,
)
from webull_skill.trading.account import normalize_account_id

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


def get_account_balance(sdk: "SDKClient", account_id: str) -> str:
    """Get account balance.

    Returns: net_liquidation, buying_power, cash_balance,
    market_value, unrealized_pnl, realized_pnl.
    """
    account_id = normalize_account_id(account_id) or ""
    try:
        response = sdk.trade.account_v2.get_account_balance(account_id)
        data = extract_response_data(response)
        return prepend_disclaimer(format_account_balance(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_account_balance")


def get_account_positions(sdk: "SDKClient", account_id: str) -> str:
    """Get account positions.

    Returns: symbol, quantity, side, avg_cost, last_price,
    market_value, unrealized_pnl, realized_pnl.
    """
    account_id = normalize_account_id(account_id) or ""
    try:
        response = sdk.trade.account_v2.get_account_position(account_id)
        data = extract_response_data(response)
        return prepend_disclaimer(format_positions(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_account_positions")


def get_account_position_details(
    sdk: "SDKClient",
    config: "SkillConfig",
    account_id: str,
    instrument_id: str,
    page_size: int = 20,
    last_id: str | None = None,
) -> str:
    """Get JP account position details for a specific instrument.

    JP-only. Required: account_id and instrument_id. Supports pagination via
    page_size and last_id.
    """
    if config.region_id.lower() != "jp":
        return "Validation error: account position details is only supported in region 'jp'"
    account_id = normalize_account_id(account_id) or ""
    if not account_id:
        return "Validation error: account_id is required"
    if not instrument_id:
        return "Validation error: instrument_id is required"
    if page_size <= 0:
        return "Validation error: page_size must be > 0"

    try:
        response = sdk.trade.account_v2.get_account_position_details(
            account_id,
            instrument_id,
            page_size=page_size,
            last_id=last_id,
        )
        data = extract_response_data(response)
        return prepend_disclaimer(format_position_details(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_account_position_details")
