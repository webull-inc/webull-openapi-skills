"""Unit tests for stock market data: bars time range and NOII."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.market_data.stock import (
    get_stock_bars,
    get_stock_bars_single,
    get_stock_noii_bars,
    get_stock_noii_snapshot,
)


class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeMarketData:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get_history_bar(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_history_bar", kwargs))
        return _FakeResponse([
            {"time": "2024-03-08", "open": "169", "high": "173", "low": "168", "close": "170", "volume": "76000000"}
        ])

    def get_batch_history_bar(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_batch_history_bar", kwargs))
        return _FakeResponse([
            {
                "symbol": "AAPL",
                "result": [
                    {"time": "2024-03-08", "open": "169", "high": "173", "low": "168", "close": "170", "volume": "76000000"}
                ],
            }
        ])

    def get_noii_bars(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_noii_bars", kwargs))
        return _FakeResponse([
            {
                "instrument_id": "913256135",
                "symbol": "AAPL",
                "imbalance_time": "1711262998500",
                "imbalance_ref_price": "172.35",
                "imbalance_near_price": "173.1",
                "imbalance_far_price": "175.5",
                "imbalance_action_type": "PRE_OPEN",
            },
            {
                "instrument_id": "913256135",
                "symbol": "AAPL",
                "imbalance_time": "1711263003500",
                "imbalance_ref_price": "172.40",
                "imbalance_near_price": "173.2",
                "imbalance_far_price": "175.6",
                "imbalance_action_type": "PRE_OPEN",
            },
        ])

    def get_noii_snapshot(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_noii_snapshot", kwargs))
        return _FakeResponse({
            "instrument_id": "913256135",
            "symbol": "AAPL",
            "paired_shares": "701859",
            "imbalance_shares": "5715",
            "imbalance_side": "2",
            "imbalance_ref_price": "253.83",
            "imbalance_near_price": "253.93",
            "imbalance_far_price": "253.98",
            "imbalance_action_type": "PRE_CLOSE",
            "imbalance_time": "1774272599000",
            "imbalance_var_indicator": "10",
        })


def _fake_sdk(market_data: _FakeMarketData) -> object:
    data = SimpleNamespace(market_data=market_data)
    return SimpleNamespace(data=data, region_id="us")


def _config() -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id="us")


# ---------------------------------------------------------------------------
# Stock bars start_time / end_time
# ---------------------------------------------------------------------------

def test_get_stock_bars_single_passes_start_end_time():
    md = _FakeMarketData()
    result = get_stock_bars_single(
        _fake_sdk(md), _config(),
        symbol="AAPL",
        category="US_STOCK",
        timespan="D",
        count=5,
        start_time=1700000000000,
        end_time=1710000000000,
    )

    assert "=== Stock Bars (OHLCV) ===" in result
    call = md.calls[0]
    assert call[0] == "get_history_bar"
    assert call[1]["start_time"] == 1700000000000
    assert call[1]["end_time"] == 1710000000000
    assert call[1]["symbol"] == "AAPL"


def test_get_stock_bars_single_omits_none_time():
    md = _FakeMarketData()
    get_stock_bars_single(
        _fake_sdk(md), _config(),
        symbol="AAPL",
        start_time=None,
        end_time=None,
    )

    call = md.calls[0]
    assert "start_time" not in call[1]
    assert "end_time" not in call[1]


def test_get_stock_bars_batch_passes_start_end_time():
    md = _FakeMarketData()
    result = get_stock_bars(
        _fake_sdk(md), _config(),
        symbols="AAPL,TSLA",
        category="US_STOCK",
        timespan="H1",
        count=10,
        start_time=1700000000000,
        end_time=1710000000000,
    )

    assert "=== Stock Bars (OHLCV) ===" in result
    call = md.calls[0]
    assert call[0] == "get_batch_history_bar"
    assert call[1]["start_time"] == 1700000000000
    assert call[1]["end_time"] == 1710000000000
    assert call[1]["symbols"] == ["AAPL", "TSLA"]


def test_get_stock_bars_batch_omits_none_time():
    md = _FakeMarketData()
    get_stock_bars(
        _fake_sdk(md), _config(),
        symbols="AAPL",
        start_time=None,
        end_time=None,
    )

    call = md.calls[0]
    assert "start_time" not in call[1]
    assert "end_time" not in call[1]


# ---------------------------------------------------------------------------
# NOII bars
# ---------------------------------------------------------------------------

def test_get_stock_noii_bars_formats_list():
    md = _FakeMarketData()
    result = get_stock_noii_bars(
        _fake_sdk(md), _config(),
        symbol="AAPL",
        category="US_STOCK",
        imbalance_action_type="PRE_OPEN",
    )

    assert "=== NOII Bars: AAPL ===" in result
    assert "Instrument ID:   913256135" in result
    assert "Symbol:          AAPL" in result
    assert "172.35" in result
    assert "173.1" in result
    assert "175.5" in result
    assert "PRE_OPEN" in result
    assert "172.40" in result
    assert md.calls[0] == ("get_noii_bars", {
        "symbol": "AAPL",
        "category": "US_STOCK",
        "imbalance_action_type": "PRE_OPEN",
    })


def test_get_stock_noii_bars_empty():
    md = _FakeMarketData()
    md.get_noii_bars = lambda **kw: _FakeResponse([])
    result = get_stock_noii_bars(_fake_sdk(md), _config(), symbol="AAPL")

    assert "No data available" in result


# ---------------------------------------------------------------------------
# NOII snapshot
# ---------------------------------------------------------------------------

def test_get_stock_noii_snapshot_formats_response():
    md = _FakeMarketData()
    result = get_stock_noii_snapshot(
        _fake_sdk(md), _config(),
        symbol="AAPL",
        category="US_STOCK",
        imbalance_action_type="PRE_CLOSE",
    )

    assert "=== NOII Snapshot: AAPL ===" in result
    assert "Instrument ID:       913256135" in result
    assert "Paired Shares:       701859" in result
    assert "Imbalance Shares:    5715" in result
    assert "Imbalance Side:      2" in result
    assert "Ref Price:           253.83" in result
    assert "Near Price:          253.93" in result
    assert "Far Price:           253.98" in result
    assert "Action Type:         PRE_CLOSE" in result
    assert "Var Indicator:       10" in result
    assert md.calls[0] == ("get_noii_snapshot", {
        "symbol": "AAPL",
        "category": "US_STOCK",
        "imbalance_action_type": "PRE_CLOSE",
    })


def test_get_stock_noii_snapshot_empty():
    md = _FakeMarketData()
    md.get_noii_snapshot = lambda **kw: _FakeResponse(None)
    result = get_stock_noii_snapshot(_fake_sdk(md), _config(), symbol="AAPL")

    assert "No data available" in result
