"""Watchlist tools for Webull OpenAPI Skill.

Provides: get_watchlist, create_watchlist, delete_watchlist, update_watchlist,
          get_watchlist_instruments, add_watchlist_instruments,
          remove_watchlist_instruments, update_watchlist_instruments.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Optional

from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_watchlist,
    format_watchlist_instruments,
    format_watchlist_result,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig
    from webull_skill.sdk_client import SDKClient


def get_watchlist(
    sdk: "SDKClient",
    config: "SkillConfig",
) -> str:
    """Get all watchlists for the current user.

    Returns: watchlist_id, name, sort, create_time, update_time.
    """
    try:
        data = extract_response_data(sdk.data.watchlist.get_watchlist())
        return prepend_disclaimer(format_watchlist(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_watchlist", config.region_id)


def create_watchlist(
    sdk: "SDKClient",
    config: "SkillConfig",
    name: str,
    sort: Optional[int] = None,
) -> str:
    """Create a new watchlist. Maximum 20 watchlists allowed.

    :param name: Watchlist name.
    :param sort: Sort order number (optional).
    Returns: watchlist_id of the newly created watchlist.
    """
    try:
        data = extract_response_data(
            sdk.data.watchlist.create_watchlist(name=name, sort=sort)
        )
        return prepend_disclaimer(format_watchlist_result(data, "Create Watchlist"))
    except Exception as e:
        return handle_sdk_exception(e, "create_watchlist", config.region_id)


def delete_watchlist(
    sdk: "SDKClient",
    config: "SkillConfig",
    watchlist_id: str,
) -> str:
    """Delete a watchlist and all instruments in it. Irreversible.

    :param watchlist_id: Watchlist unique identifier.
    """
    try:
        data = extract_response_data(
            sdk.data.watchlist.delete_watchlist(watchlist_id=watchlist_id)
        )
        return prepend_disclaimer(format_watchlist_result(data, "Delete Watchlist"))
    except Exception as e:
        return handle_sdk_exception(e, "delete_watchlist", config.region_id)


def update_watchlist(
    sdk: "SDKClient",
    config: "SkillConfig",
    watchlist_id: str,
    name: Optional[str] = None,
    sort: Optional[int] = None,
) -> str:
    """Update an existing watchlist's name or sort order.

    :param watchlist_id: Watchlist unique identifier.
    :param name: New watchlist name (optional).
    :param sort: New sort order number (optional).
    """
    try:
        data = extract_response_data(
            sdk.data.watchlist.update_watchlist(
                watchlist_id=watchlist_id, name=name, sort=sort
            )
        )
        return prepend_disclaimer(format_watchlist_result(data, "Update Watchlist"))
    except Exception as e:
        return handle_sdk_exception(e, "update_watchlist", config.region_id)


def get_watchlist_instruments(
    sdk: "SDKClient",
    config: "SkillConfig",
    watchlist_id: str,
) -> str:
    """Get all instruments in a watchlist.

    :param watchlist_id: Watchlist unique identifier.
    Returns: instrument_id, symbol, name, exchange_code, sort, added_time.
    """
    try:
        data = extract_response_data(
            sdk.data.watchlist.get_instruments(watchlist_id=watchlist_id)
        )
        return prepend_disclaimer(format_watchlist_instruments(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_watchlist_instruments", config.region_id)


def add_watchlist_instruments(
    sdk: "SDKClient",
    config: "SkillConfig",
    watchlist_id: str,
    instruments: list[dict[str, Any]],
) -> str:
    """Add instruments to a watchlist. Max 1000 instruments total across all watchlists.

    Does not support EC event contracts, futures, or options.

    :param watchlist_id: Watchlist unique identifier.
    :param instruments: List of dicts with keys: symbol, category, sort (optional).
        Example: [{"symbol": "AAPL", "category": "US_STOCK", "sort": 1}]
    """
    try:
        data = extract_response_data(
            sdk.data.watchlist.add_instruments(
                watchlist_id=watchlist_id, instruments=instruments
            )
        )
        return prepend_disclaimer(format_watchlist_result(data, "Add Instruments"))
    except Exception as e:
        return handle_sdk_exception(e, "add_watchlist_instruments", config.region_id)


def remove_watchlist_instruments(
    sdk: "SDKClient",
    config: "SkillConfig",
    watchlist_id: str,
    instruments: list[dict[str, Any]],
) -> str:
    """Remove instruments from a watchlist.

    :param watchlist_id: Watchlist unique identifier.
    :param instruments: List of dicts with keys: symbol, category.
        Example: [{"symbol": "AAPL", "category": "US_STOCK"}]
    """
    try:
        data = extract_response_data(
            sdk.data.watchlist.remove_instruments(
                watchlist_id=watchlist_id, instruments=instruments
            )
        )
        return prepend_disclaimer(format_watchlist_result(data, "Remove Instruments"))
    except Exception as e:
        return handle_sdk_exception(e, "remove_watchlist_instruments", config.region_id)


def update_watchlist_instruments(
    sdk: "SDKClient",
    config: "SkillConfig",
    watchlist_id: str,
    instruments: list[dict[str, Any]],
) -> str:
    """Update the sort order of instruments in a watchlist.

    :param watchlist_id: Watchlist unique identifier.
    :param instruments: List of dicts with keys: symbol, category, sort.
        Example: [{"symbol": "AAPL", "category": "US_STOCK", "sort": 2}]
    """
    try:
        data = extract_response_data(
            sdk.data.watchlist.update_instruments(
                watchlist_id=watchlist_id, instruments=instruments
            )
        )
        return prepend_disclaimer(format_watchlist_result(data, "Update Instruments"))
    except Exception as e:
        return handle_sdk_exception(e, "update_watchlist_instruments", config.region_id)
