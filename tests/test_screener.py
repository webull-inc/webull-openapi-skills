"""Unit tests for market_data.screener."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from webull.core.exception.exceptions import ServerException

from webull_skill.config import SkillConfig
from webull_skill.errors import handle_sdk_exception
from webull_skill.market_data.screener import (
    get_gainers_losers,
    get_market_sentiment,
    get_most_active,
    get_stock_unusual_activities,
)


class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeScreener:
    def __init__(self) -> None:
        self.gainers_calls: list[dict] = []
        self.active_calls: list[dict] = []

    def list_gainers_losers(self, **kwargs: object) -> _FakeResponse:
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

    def list_most_active(self, **kwargs: object) -> _FakeResponse:
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
    screener.list_gainers_losers = lambda **kw: _FakeResponse({"data": [], "has_more": False})
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


class _FakeScreenerExt:
    """Records calls to the US-only screener methods."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def get_fear_and_greed_index(self, *args: object, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_fear_and_greed_index", args, kwargs))
        return _FakeResponse({
            "current": {"fear_greed_index": 43, "grade": "Neutral"},
            "previous_day": {"fear_greed_index": 55, "grade": "Neutral"},
            "time_zone": "America/New_York",
        })

    def get_stock_unusual_activities(self, *args: object, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_stock_unusual_activities", args, kwargs))
        return _FakeResponse({
            "data": [{"symbol": "NVDA", "alert_type": "VOLUME_SURGE"}]
        })


def _fake_sdk_ext(screener: _FakeScreenerExt) -> object:
    data = SimpleNamespace(screener=screener)
    return SimpleNamespace(data=data, region_id="us")


def test_market_sentiment_uses_us_category():
    screener = _FakeScreenerExt()
    sdk = _fake_sdk_ext(screener)
    result = get_market_sentiment(sdk, _config())

    assert "=== Market Sentiment Index ===" in result
    assert "43" in result
    name, args, kwargs = screener.calls[0]
    assert name == "get_fear_and_greed_index"
    assert args == ()
    assert kwargs == {"category": "US_STOCK"}


def test_stock_unusual_activities_builds_kwargs():
    screener = _FakeScreenerExt()
    sdk = _fake_sdk_ext(screener)
    result = get_stock_unusual_activities(sdk, _config(), symbol="NVDA", count=5,
                                          extended_hours_required=True)

    assert "=== Stock Unusual Activities ===" in result
    name, args, kwargs = screener.calls[0]
    assert name == "get_stock_unusual_activities"
    assert args == ()
    assert kwargs == {
        "category": "US_STOCK", "count": 5, "symbol": "NVDA",
        "alert_types": None, "extended_hours_required": True,
    }


# ---------------------------------------------------------------------------
# count range validation (1-30, local before hitting the SDK)
# ---------------------------------------------------------------------------

def test_stock_unusual_activities_rejects_count_below_range():
    screener = _FakeScreenerExt()
    sdk = _fake_sdk_ext(screener)
    result = get_stock_unusual_activities(sdk, _config(), count=0)
    assert "count must be between 1 and 30" in result
    assert screener.calls == []  # SDK not called


def test_stock_unusual_activities_rejects_count_above_range():
    screener = _FakeScreenerExt()
    sdk = _fake_sdk_ext(screener)
    result = get_stock_unusual_activities(sdk, _config(), count=31)
    assert "count must be between 1 and 30" in result
    assert screener.calls == []  # SDK not called


def test_stock_unusual_activities_accepts_count_boundaries():
    for boundary in (1, 30):
        screener = _FakeScreenerExt()
        sdk = _fake_sdk_ext(screener)
        result = get_stock_unusual_activities(sdk, _config(), count=boundary)
        assert "=== Stock Unusual Activities ===" in result
        assert len(screener.calls) == 1


@pytest.mark.parametrize(
    "tool_name,http_status",
    [
        ("get_market_sentiment", 401),
        ("get_stock_unusual_activities", 403),
    ],
)
def test_new_screener_tools_return_subscription_hint(tool_name: str, http_status: int):
    error = ServerException(
        "MARKET_DATA_NOT_SUBSCRIBED", "subscription required", http_status=http_status
    )

    result = handle_sdk_exception(error, tool_name, "us")

    assert "Market data requires quotes subscription." in result
    assert "https://www.webullapp.com/quote" in result
