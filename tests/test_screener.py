"""Unit tests for market_data.screener."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.market_data.screener import get_gainers_losers, get_most_active


class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeScreener:
    def __init__(self) -> None:
        self.gainers_calls: list[dict] = []
        self.active_calls: list[dict] = []

    def get_gainers_losers(self, **kwargs: object) -> _FakeResponse:
        self.gainers_calls.append(kwargs)
        return _FakeResponse({
            "data": [
                {
                    "instrument_id": "913256135",
                    "symbol": "TSLA",
                    "name": "Tesla Inc",
                    "exchange_code": "NSQ",
                    "currency_code": "USD",
                    "price": "250.00",
                    "pre_close": "240.00",
                    "open": "242.00",
                    "high": "255.00",
                    "low": "241.00",
                    "close": "250.00",
                    "change": "10.00",
                    "change_ratio": "0.0417",
                    "volume": "5000000",
                    "turnover": "1250000000",
                    "turnover_rate": "0.05",
                    "market_value": "800000000000",
                    "amplitude": "0.0583",
                }
            ],
            "has_more": False,
        })

    def get_most_active(self, **kwargs: object) -> _FakeResponse:
        self.active_calls.append(kwargs)
        return _FakeResponse({
            "data": [
                {
                    "instrument_id": "913256136",
                    "symbol": "NVDA",
                    "name": "Nvidia Corporation",
                    "exchange_code": "NSQ",
                    "currency_code": "USD",
                    "price": "130.00",
                    "pre_close": "128.00",
                    "open": "129.00",
                    "high": "132.00",
                    "low": "127.00",
                    "close": "130.00",
                    "change": "2.00",
                    "change_ratio": "0.0156",
                    "volume": "100000000",
                    "turnover": "13000000000",
                    "turnover_rate": "0.04",
                    "market_value": "3200000000000",
                    "amplitude": "0.0391",
                    "relative_volume_10d": "1.5",
                }
            ],
            "has_more": True,
        })


def _fake_sdk(screener: _FakeScreener) -> object:
    data = SimpleNamespace(screener=screener)
    return SimpleNamespace(data=data, region_id="us")


def _config() -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id="us")


def test_get_gainers_losers_formats_response():
    screener = _FakeScreener()
    sdk = _fake_sdk(screener)
    result = get_gainers_losers(
        sdk, _config(),
        rank_type="DAY_1",
        category="US_STOCK",
        sort_by="CHANGE_RATIO",
        direction="DESC",
        page_index=1,
        page_size=20,
    )

    assert "=== Gainers / Losers ===" in result
    assert "913256135" in result
    assert "TSLA" in result
    assert "Tesla Inc" in result
    assert "250.00" in result
    assert "0.0417" in result
    assert "Turnover:        1250000000" in result
    assert "[Has More: No]" in result
    assert screener.gainers_calls[0]["rank_type"] == "DAY_1"
    assert screener.gainers_calls[0]["direction"] == "DESC"


def test_get_gainers_losers_empty_data():
    screener = _FakeScreener()
    screener.get_gainers_losers = lambda **kw: _FakeResponse({"data": [], "has_more": False})
    sdk = _fake_sdk(screener)
    result = get_gainers_losers(sdk, _config(), rank_type="DAY_1", category="US_STOCK", sort_by="CHANGE_RATIO")

    assert "No data available" in result


def test_get_most_active_formats_response():
    screener = _FakeScreener()
    sdk = _fake_sdk(screener)
    result = get_most_active(
        sdk, _config(),
        category="US_STOCK",
        rank_type="VOLUME",
        sort_by="VOLUME",
        direction="DESC",
    )

    assert "=== Most Active ===" in result
    assert "NVDA" in result
    assert "Turnover:        13000000000" in result
    assert "Rel Vol 10D:     1.5" in result
    assert "[Has More: Yes]" in result
    assert screener.active_calls[0]["rank_type"] == "VOLUME"
