"""Account tools for Webull OpenAPI Skill.

Provides: get_account_list, resolve_account_id.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from webull_skill.constants import ASSET_TYPE_ACCOUNT_LABELS, JP_STOCK_ACCOUNT_TYPES
from webull_skill.errors import handle_sdk_exception
from webull_skill.formatters import (
    extract_response_data,
    format_account_list,
    prepend_disclaimer,
)

if TYPE_CHECKING:
    from webull_skill.sdk_client import SDKClient


def normalize_account_id(account_id: object | None) -> str | None:
    """Normalize account_id to a stripped string for SDK calls and comparisons."""
    if account_id is None:
        return None
    return str(account_id).strip()


def get_account_list(sdk: "SDKClient") -> str:
    """Get all linked accounts.

    Returns: account_id, account_number, account_type, account_class, account_label.
    """
    try:
        response = sdk.trade.account_v2.get_account_list()
        data = extract_response_data(response)
        return prepend_disclaimer(format_account_list(data))
    except Exception as e:
        return handle_sdk_exception(e, "get_account_list")


def _sdk_region_id(sdk: "SDKClient") -> str:
    """Read region id from SDKClient without depending on its concrete type."""
    return str(getattr(sdk, "region_id", "")).lower()


def _is_jp_stock_asset(region_id: str, asset_type: str) -> bool:
    """JP stock accounts are identified by account_type instead of label."""
    return region_id == "jp" and asset_type in {"stock", "option"}


def get_account_by_id(sdk: "SDKClient", account_id: str) -> dict | None:
    """Return a single accountList item by account_id, or None if absent."""
    normalized_account_id = normalize_account_id(account_id)
    if not normalized_account_id:
        return None
    response = sdk.trade.account_v2.get_account_list()
    accounts = extract_response_data(response)
    if not isinstance(accounts, list):
        return None
    for acct in accounts:
        if (
            isinstance(acct, dict)
            and normalize_account_id(acct.get("account_id")) == normalized_account_id
        ):
            return acct
    return None


def _validate_explicit_account(
    accounts: list[dict],
    account_id: str,
    valid_labels: set[str],
    asset_type: str,
    region_id: str = "",
) -> None:
    """Validate an explicitly provided account_id against the required labels."""
    normalized_account_id = normalize_account_id(account_id)
    for acct in accounts:
        if normalize_account_id(acct.get("account_id")) == normalized_account_id:
            if _is_jp_stock_asset(region_id, asset_type):
                account_type = acct.get("account_type", "")
                if account_type not in JP_STOCK_ACCOUNT_TYPES:
                    expected = ", ".join(sorted(JP_STOCK_ACCOUNT_TYPES))
                    raise ValueError(
                        f"Account '{account_id}' (account_type: {account_type or 'N/A'}) "
                        f"does not support {asset_type} trading. "
                        f"Required account_type values: {expected}."
                    )
                return
            label = acct.get("account_label", "")
            if label and label not in valid_labels:
                expected = ", ".join(sorted(valid_labels))
                raise ValueError(
                    f"Account '{account_id}' (label: {label}) does not support {asset_type} trading. "
                    f"Required account types: {expected}. "
                    f"Please use get_account_list to find the correct account."
                )
            return

    raise ValueError(
        f"Account '{normalized_account_id or account_id}' was not found. "
        f"Please use get_account_list to find a valid account_id."
    )


def _auto_select_account(
    accounts: list[dict],
    valid_labels: set[str],
    asset_type: str,
    region_id: str = "",
) -> str:
    """Auto-select an account matching the required labels."""
    if _is_jp_stock_asset(region_id, asset_type):
        matching = [
            acct for acct in accounts
            if acct.get("account_type", "") in JP_STOCK_ACCOUNT_TYPES
        ]
    else:
        matching = [
            acct for acct in accounts
            if acct.get("account_label", "") in valid_labels
        ]

    if len(matching) == 1:
        account_id = normalize_account_id(matching[0].get("account_id"))
        if account_id:
            return account_id
        raise ValueError(f"Matched {asset_type} account is missing account_id.")

    if len(matching) > 1:
        acct_list = ", ".join(
            f"{normalize_account_id(a.get('account_id')) or a.get('account_id')} "
            f"({a.get('account_type') or a.get('account_label', 'N/A')})"
            for a in matching
        )
        raise ValueError(
            f"Multiple {asset_type} accounts found: {acct_list}. "
            f"Please specify account_id explicitly."
        )

    expected = (
        ", ".join(sorted(JP_STOCK_ACCOUNT_TYPES))
        if _is_jp_stock_asset(region_id, asset_type)
        else ", ".join(sorted(valid_labels))
    )
    raise ValueError(
        f"No account found for {asset_type} trading. "
        f"Required account types: {expected}."
    )


def resolve_account_id(
    sdk: "SDKClient",
    asset_type: str,
    account_id: str | None = None,
) -> str:
    """Resolve and validate the correct account_id for a given asset type.

    - If account_id is provided, validates it matches the required asset type.
    - If not provided, auto-selects the first matching account.
    - For single-account setups (e.g., HK region), uses that account directly.
    """
    valid_labels = ASSET_TYPE_ACCOUNT_LABELS.get(asset_type)
    if valid_labels is None:
        raise ValueError(f"Unknown asset_type '{asset_type}'")
    account_id = normalize_account_id(account_id)
    region_id = _sdk_region_id(sdk)

    response = sdk.trade.account_v2.get_account_list()
    accounts = extract_response_data(response)

    if not accounts or not isinstance(accounts, list):
        raise ValueError("No accounts found. Please check your API credentials.")

    if len(accounts) == 1:
        normalized = normalize_account_id(accounts[0].get("account_id"))
        if normalized:
            return normalized
        raise ValueError("The only available account is missing account_id.")

    if account_id:
        _validate_explicit_account(accounts, account_id, valid_labels, asset_type, region_id)
        return account_id

    return _auto_select_account(accounts, valid_labels, asset_type, region_id)
