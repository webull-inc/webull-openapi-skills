"""Unit tests for trading.account."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from webull_skill.trading.account import resolve_account_id


def _fake_sdk(region_id: str, accounts: list[dict]) -> object:
    account_v2 = SimpleNamespace(get_account_list=lambda: accounts)
    trade = SimpleNamespace(account_v2=account_v2)
    return SimpleNamespace(region_id=region_id, trade=trade)


def test_resolve_jp_stock_account_uses_account_type_not_label():
    sdk = _fake_sdk(
        "jp",
        [
            {
                "account_id": "jp-margin",
                "account_type": "US_MARGIN",
                "account_label": "Unexpected Label",
            },
            {
                "account_id": "other",
                "account_type": "FX",
                "account_label": "Individual Cash",
            },
        ],
    )

    assert resolve_account_id(sdk, "stock") == "jp-margin"


def test_resolve_jp_stock_account_rejects_invalid_account_type():
    sdk = _fake_sdk(
        "jp",
        [
            {
                "account_id": "bad-account",
                "account_type": "FX",
                "account_label": "Individual Cash",
            },
            {
                "account_id": "jp-cash",
                "account_type": "CASH",
                "account_label": "Anything",
            },
        ],
    )

    with pytest.raises(ValueError, match="does not support stock trading"):
        resolve_account_id(sdk, "stock", account_id="bad-account")


def test_resolve_account_id_accepts_int_explicit_account_id():
    sdk = _fake_sdk(
        "us",
        [
            {
                "account_id": "123",
                "account_type": "CASH",
                "account_label": "Individual Cash",
            },
            {
                "account_id": "456",
                "account_type": "CASH",
                "account_label": "Roth IRA",
            },
        ],
    )

    assert resolve_account_id(sdk, "stock", account_id=123) == "123"


def test_resolve_account_id_rejects_unknown_explicit_account_id():
    sdk = _fake_sdk(
        "us",
        [
            {
                "account_id": "123",
                "account_type": "CASH",
                "account_label": "Individual Cash",
            },
            {
                "account_id": "456",
                "account_type": "CASH",
                "account_label": "Roth IRA",
            },
        ],
    )

    with pytest.raises(ValueError, match="was not found"):
        resolve_account_id(sdk, "stock", account_id=999)
