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
                "account_class": "INDIVIDUAL_MARGIN",
            },
            {
                "account_id": "other",
                "account_type": "FX",
                "account_class": "INDIVIDUAL_CASH",
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
                "account_class": "INDIVIDUAL_CASH",
            },
            {
                "account_id": "jp-cash",
                "account_type": "CASH",
                "account_class": "INDIVIDUAL_CASH",
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
                "account_class": "INDIVIDUAL_CASH",
            },
            {
                "account_id": "456",
                "account_type": "CASH",
                "account_class": "ROTH_IRA",
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
                "account_class": "INDIVIDUAL_CASH",
            },
            {
                "account_id": "456",
                "account_type": "CASH",
                "account_class": "ROTH_IRA",
            },
        ],
    )

    with pytest.raises(ValueError, match="was not found"):
        resolve_account_id(sdk, "stock", account_id=999)


def _jp_accounts() -> list[dict]:
    return [
        {"account_id": "jp-cash", "account_type": "CASH", "account_class": "INDIVIDUAL_CASH"},
        {"account_id": "jp-margin", "account_type": "US_MARGIN", "account_class": "INDIVIDUAL_MARGIN"},
        {"account_id": "jp-option", "account_type": "US_OPTION", "account_class": "INDIVIDUAL_US_OPTION"},
    ]


def test_resolve_jp_option_account_accepts_explicit_us_option_account():
    sdk = _fake_sdk("jp", _jp_accounts())

    assert resolve_account_id(sdk, "option", account_id="jp-option") == "jp-option"


def test_resolve_jp_option_account_rejects_explicit_cash_account():
    sdk = _fake_sdk("jp", _jp_accounts())

    with pytest.raises(ValueError, match="US_OPTION"):
        resolve_account_id(sdk, "option", account_id="jp-cash")


def test_resolve_jp_option_account_auto_selects_us_option_account():
    sdk = _fake_sdk("jp", _jp_accounts())

    assert resolve_account_id(sdk, "option") == "jp-option"


def test_resolve_jp_option_account_fails_without_us_option_account():
    accounts = [acct for acct in _jp_accounts() if acct["account_type"] != "US_OPTION"]
    sdk = _fake_sdk("jp", accounts)

    with pytest.raises(ValueError, match="No account found for option trading"):
        resolve_account_id(sdk, "option")


def test_resolve_jp_stock_account_still_matches_cash_and_us_margin():
    sdk = _fake_sdk("jp", _jp_accounts())

    assert resolve_account_id(sdk, "stock", account_id="jp-cash") == "jp-cash"
    assert resolve_account_id(sdk, "stock", account_id="jp-margin") == "jp-margin"
    with pytest.raises(ValueError, match="does not support stock trading"):
        resolve_account_id(sdk, "stock", account_id="jp-option")
