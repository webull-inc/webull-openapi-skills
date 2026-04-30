"""Unit tests for trading.assets."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.trading.assets import get_account_position_details


class _FakeAccountV2:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def get_account_position_details(
        self,
        account_id: str,
        instrument_id: str,
        page_size: int | None = None,
        last_id: str | None = None,
    ) -> dict:
        self.calls.append({
            "account_id": account_id,
            "instrument_id": instrument_id,
            "page_size": page_size,
            "last_id": last_id,
        })
        return [
            {
                "id": "037A1DU2HO6DT0KHK0C8000000",
                "quantity": "100",
                "market_value": "10000",
                "symbol": "AAPL",
                "symbol_name": "Apple Inc.",
                "currency": "USD",
                "account_tax_type": "GENERAL",
                "instrument_id": "481004076",
                "contract_id": "contract-1",
                "hold_type": "LONG",
                "margin_type": "ONE_DAY",
                "average_price": "100",
                "unrealized_pl": "550",
                "base_currency": "JPY",
                "fx_rate": "146.48",
                "base_currency_market_value": "1628.85",
                "exchange_code": "NASDAQ",
            }
        ]


def _fake_sdk(account_v2: _FakeAccountV2) -> object:
    trade = SimpleNamespace(account_v2=account_v2)
    return SimpleNamespace(trade=trade)


def test_account_position_details_is_jp_only():
    result = get_account_position_details(
        _fake_sdk(_FakeAccountV2()),
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        account_id="acct-1",
        instrument_id="9001",
    )

    assert result == "Validation error: account position details is only supported in region 'jp'"


def test_account_position_details_calls_sdk_and_formats_response():
    account_v2 = _FakeAccountV2()
    result = get_account_position_details(
        _fake_sdk(account_v2),
        SkillConfig(app_key="k", app_secret="s", region_id="jp"),
        account_id=123,
        instrument_id="9001",
        page_size=25,
        last_id="cursor-1",
    )

    assert account_v2.calls == [{
        "account_id": "123",
        "instrument_id": "9001",
        "page_size": 25,
        "last_id": "cursor-1",
    }]
    assert "=== Position Details ===" in result
    assert "[Position Detail 1]" in result
    assert "AAPL  Qty:      100  Hold:   LONG  Market Value:      10000  Currency: USD" in result
    assert "Name: Apple Inc.  Exchange: NASDAQ" in result
    assert "Average Price:        100  Unrealized P&L:        550" in result
    assert "Account Tax Type: GENERAL  Margin Type: ONE_DAY" in result
    assert "Instrument ID: 481004076  Contract ID: contract-1  Position ID: 037A1DU2HO6DT0KHK0C8000000" in result
    assert "Base Currency: JPY  FX Rate: 146.48  Base Currency Market Value: 1628.85" in result
