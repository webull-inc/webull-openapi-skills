"""Unit tests for trading.order."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from webull_skill.trading.order import cancel_order, get_open_orders, get_order_history


class _FakeOrderV3:
    def __init__(self) -> None:
        self.cancel_calls: list[dict] = []

    def list_order_history(self, **kwargs: object) -> dict:
        self.history_calls = getattr(self, "history_calls", [])
        self.history_calls.append(kwargs)
        return {"data": [{"client_order_id": "c1", "combo_type": "NORMAL"}], "pagination_key": "next-h"}

    def list_order_open(self, **kwargs: object) -> dict:
        self.open_calls = getattr(self, "open_calls", [])
        self.open_calls.append(kwargs)
        return {"data": [{"client_order_id": "c2", "combo_type": "NORMAL"}]}

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


def test_get_order_history_uses_v3_list_with_time_range_and_cursor():
    order_v3 = _FakeOrderV3()
    sdk = SimpleNamespace(trade=SimpleNamespace(order_v3=order_v3))
    result = get_order_history(
        sdk,
        account_id=123,
        start_time="2025-01-05T00:00:00Z",
        end_time="2025-01-06T00:00:00.500Z",
        pagination_key="pk-1",
    )
    assert order_v3.history_calls == [{
        "account_id": "123",
        "start_time": "2025-01-05T00:00:00.000Z",
        "end_time": "2025-01-06T00:00:00.500Z",
        "pagination_key": "pk-1",
    }]
    assert "Client Order ID:  c1" in result
    assert "Next pagination_key: next-h" in result


def test_get_open_orders_uses_v3_list_and_omits_unset_cursor():
    order_v3 = _FakeOrderV3()
    sdk = SimpleNamespace(trade=SimpleNamespace(order_v3=order_v3))
    result = get_open_orders(sdk, account_id="acct-1")
    assert order_v3.open_calls == [{"account_id": "acct-1"}]
    assert "Client Order ID:  c2" in result
    assert "Next pagination_key" not in result


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2025-01-05T00:00:00Z", "2025-01-05T00:00:00.000Z"),
        ("2025-01-05T00:00:00.500Z", "2025-01-05T00:00:00.500Z"),
        # Not second-precision UTC: passed through unchanged so the server validates it.
        ("2025-01-05T00:00Z", "2025-01-05T00:00Z"),
        ("2025-01-05", "2025-01-05"),
        ("2025-01-05T00:00:00+08:00", "2025-01-05T00:00:00+08:00"),
        ("abc", "abc"),
    ],
)
def test_normalize_iso_utc_millis_only_upgrades_second_precision(value, expected):
    from webull_skill.trading.order import _normalize_iso_utc_millis

    assert _normalize_iso_utc_millis(value) == expected
