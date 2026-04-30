"""Unit tests for trading.order."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.trading.order import cancel_order


class _FakeOrderV3:
    def __init__(self) -> None:
        self.cancel_calls: list[dict] = []

    def cancel_order(self, *, account_id: str, client_order_id: str) -> dict:
        self.cancel_calls.append({
            "account_id": account_id,
            "client_order_id": client_order_id,
        })
        return {"client_order_id": client_order_id, "order_id": "o1"}


def test_cancel_order_accepts_int_account_id():
    order_v3 = _FakeOrderV3()
    sdk = SimpleNamespace(trade=SimpleNamespace(order_v3=order_v3))

    result = cancel_order(sdk, account_id=123, client_order_id="abc123")

    assert "Order cancelled:" in result
    assert order_v3.cancel_calls == [{
        "account_id": "123",
        "client_order_id": "abc123",
    }]
