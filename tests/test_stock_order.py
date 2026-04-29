"""Unit tests for JP stock-order extensions."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.trading.stock_order import (
    place_stock_order,
    preview_stock_order,
    replace_stock_order,
)


class _FakeOrderV3:
    def __init__(self) -> None:
        self.place_calls: list[dict] = []
        self.preview_calls: list[dict] = []
        self.replace_calls: list[dict] = []

    def place_order(self, *, account_id: str, new_orders: list[dict], **kwargs: object) -> dict:
        self.place_calls.append({
            "account_id": account_id,
            "new_orders": new_orders,
            **kwargs,
        })
        return {"client_order_id": "c1", "order_id": "o1"}

    def preview_order(self, *, account_id: str, preview_orders: list[dict]) -> dict:
        self.preview_calls.append({
            "account_id": account_id,
            "preview_orders": preview_orders,
        })
        return {"estimated_amount": "100.00", "currency": "USD"}

    def replace_order(self, *, account_id: str, modify_orders: list[dict]) -> dict:
        self.replace_calls.append({
            "account_id": account_id,
            "modify_orders": modify_orders,
        })
        return {"client_order_id": "c1", "order_id": "o1"}


def _fake_sdk(
    account_type: str,
    *,
    account_id: str = "acct-1",
    account_label: str = "Anything",
    region_id: str = "jp",
) -> tuple[object, _FakeOrderV3]:
    order_v3 = _FakeOrderV3()
    account_v2 = SimpleNamespace(
        get_account_list=lambda: [
            {
                "account_id": account_id,
                "account_type": account_type,
                "account_label": account_label,
            }
        ]
    )
    trade = SimpleNamespace(account_v2=account_v2, order_v3=order_v3)
    return SimpleNamespace(region_id=region_id, trade=trade), order_v3


def test_preview_stock_order_requires_account_tax_type_for_jp():
    sdk, _ = _fake_sdk("US_MARGIN")
    result = preview_stock_order(
        sdk,
        account_id="acct-1",
        symbol="AAPL",
        side="BUY",
        order_type="LIMIT",
        time_in_force="DAY",
        quantity=1,
        market="US",
        limit_price=100,
        config=SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert result == "Validation error: account_tax_type is required for JP stock orders"


def test_preview_stock_order_rejects_margin_fields_for_cash_account():
    sdk, _ = _fake_sdk("CASH")
    result = preview_stock_order(
        sdk,
        account_id="acct-1",
        symbol="AAPL",
        side="BUY",
        order_type="LIMIT",
        time_in_force="DAY",
        quantity=1,
        market="US",
        limit_price=100,
        account_tax_type="GENERAL",
        margin_type="ONE_DAY",
        config=SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert result == "Validation error: margin_type and position_intent are not allowed for JP CASH accounts"


def test_preview_stock_order_forwards_jp_fields_and_support_trading_session():
    sdk, order_v3 = _fake_sdk("US_MARGIN")
    result = preview_stock_order(
        sdk,
        account_id="acct-1",
        symbol="AAPL",
        side="BUY",
        order_type="STOP_LOSS_LIMIT",
        time_in_force="GTC",
        quantity=1,
        market="US",
        limit_price=101,
        stop_price=99,
        support_trading_session="NIGHT",
        account_tax_type="GENERAL",
        margin_type="ONE_DAY",
        position_intent="BUY_TO_OPEN",
        close_contracts=[{"contract_id": "c-1", "quantity": 10}],
        config=SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert "=== Order Preview ===" in result
    call = order_v3.preview_calls[0]
    assert call["account_id"] == "acct-1"
    assert call["preview_orders"][0]["support_trading_session"] == "NIGHT"
    assert call["preview_orders"][0]["account_tax_type"] == "GENERAL"
    assert call["preview_orders"][0]["margin_type"] == "ONE_DAY"
    assert call["preview_orders"][0]["position_intent"] == "BUY_TO_OPEN"
    assert call["preview_orders"][0]["close_contracts"] == [
        {"contract_id": "c-1", "quantity": "10"}
    ]


def test_preview_stock_order_accepts_int_account_id():
    sdk, order_v3 = _fake_sdk("US_MARGIN", account_id="1")
    result = preview_stock_order(
        sdk,
        account_id=1,
        symbol="AAPL",
        side="BUY",
        order_type="LIMIT",
        time_in_force="DAY",
        quantity=1,
        market="US",
        limit_price=100,
        account_tax_type="GENERAL",
        config=SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert "=== Order Preview ===" in result
    assert order_v3.preview_calls[0]["account_id"] == "1"


def test_place_stock_order_accepts_int_account_id():
    sdk, order_v3 = _fake_sdk(
        "CASH",
        account_id="1",
        account_label="Individual Cash",
        region_id="us",
    )
    result = place_stock_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        symbol="AAPL",
        side="BUY",
        order_type="LIMIT",
        time_in_force="DAY",
        quantity=1,
        market="US",
        limit_price=100,
        account_id=1,
    )

    assert "client_order_id: c1" in result
    assert order_v3.place_calls[0]["account_id"] == "1"


def test_place_stock_order_uses_support_trading_session_payload_field():
    sdk, order_v3 = _fake_sdk(
        "CASH",
        account_label="Individual Cash",
        region_id="us",
    )
    result = place_stock_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        symbol="AAPL",
        side="BUY",
        order_type="LIMIT",
        time_in_force="DAY",
        quantity=1,
        market="US",
        limit_price=100,
        account_id="acct-1",
        trading_session="NIGHT",
    )

    assert "client_order_id: c1" in result
    order = order_v3.place_calls[0]["new_orders"][0]
    assert order["support_trading_session"] == "NIGHT"
    assert "trading_session" not in order


def test_replace_stock_order_rejects_close_contracts_outside_jp():
    result = replace_stock_order(
        SimpleNamespace(),
        account_id="acct-1",
        client_order_id="abc123",
        close_contracts=[{"contract_id": "c-1", "quantity": 1}],
        config=SkillConfig(app_key="k", app_secret="s", region_id="us"),
    )

    assert result == "Validation error: close_contracts is a JP-only field"


def test_replace_stock_order_accepts_int_account_id():
    sdk, order_v3 = _fake_sdk("US_MARGIN")
    result = replace_stock_order(
        sdk,
        account_id=123,
        client_order_id="abc123",
        quantity=2,
        config=SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert "client_order_id: c1" in result
    assert order_v3.replace_calls[0]["account_id"] == "123"
