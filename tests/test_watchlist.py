"""Unit tests for market_data.watchlist."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.market_data.watchlist import (
    get_watchlist,
    create_watchlist,
    delete_watchlist,
    update_watchlist,
    get_watchlist_instruments,
    add_watchlist_instruments,
    remove_watchlist_instruments,
    update_watchlist_instruments,
)


class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeWatchlist:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get_watchlist(self) -> _FakeResponse:
        self.calls.append(("get_watchlist", {}))
        return _FakeResponse([
            {
                "watchlist_id": "wl-1",
                "name": "My Stocks",
                "sort": 1,
                "create_time": "2026-01-01T00:00:00Z",
                "update_time": "2026-01-02T00:00:00Z",
            }
        ])

    def create_watchlist(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("create_watchlist", kwargs))
        return _FakeResponse({"watchlist_id": "wl-new"})

    def delete_watchlist(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("delete_watchlist", kwargs))
        return _FakeResponse(None)

    def update_watchlist(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("update_watchlist", kwargs))
        return _FakeResponse(None)

    def get_instruments(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_instruments", kwargs))
        return _FakeResponse({
            "watchlist_id": "wl-1",
            "instruments": [
                {
                    "instrument_id": "913256135",
                    "symbol": "AAPL",
                    "name": "Apple Inc",
                    "exchange_code": "NSQ",
                    "sort": 1,
                    "added_time": "2026-01-01T00:00:00Z",
                }
            ],
        })

    def add_instruments(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("add_instruments", kwargs))
        return _FakeResponse(None)

    def remove_instruments(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("remove_instruments", kwargs))
        return _FakeResponse(None)

    def update_instruments(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("update_instruments", kwargs))
        return _FakeResponse(None)


def _fake_sdk(watchlist: _FakeWatchlist) -> object:
    data = SimpleNamespace(watchlist=watchlist)
    return SimpleNamespace(data=data, region_id="us")


def _config() -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id="us")


def test_get_watchlist_formats_list():
    wl = _FakeWatchlist()
    result = get_watchlist(_fake_sdk(wl), _config())

    assert "=== Watchlists ===" in result
    assert "wl-1" in result
    assert "My Stocks" in result


def test_create_watchlist_returns_id():
    wl = _FakeWatchlist()
    result = create_watchlist(_fake_sdk(wl), _config(), name="New List", sort=5)

    assert "wl-new" in result
    assert wl.calls[0] == ("create_watchlist", {"name": "New List", "sort": 5})


def test_delete_watchlist_success():
    wl = _FakeWatchlist()
    result = delete_watchlist(_fake_sdk(wl), _config(), watchlist_id="wl-1")

    assert "Delete Watchlist" in result
    assert "Success" in result
    assert wl.calls[0] == ("delete_watchlist", {"watchlist_id": "wl-1"})


def test_update_watchlist_passes_params():
    wl = _FakeWatchlist()
    result = update_watchlist(_fake_sdk(wl), _config(), watchlist_id="wl-1", name="Renamed", sort=10)

    assert "Update Watchlist" in result
    assert wl.calls[0] == ("update_watchlist", {"watchlist_id": "wl-1", "name": "Renamed", "sort": 10})


def test_get_watchlist_instruments_formats_response():
    wl = _FakeWatchlist()
    result = get_watchlist_instruments(_fake_sdk(wl), _config(), watchlist_id="wl-1")

    assert "=== Watchlist Instruments" in result
    assert "AAPL" in result
    assert "Apple Inc" in result
    assert "913256135" in result


def test_add_watchlist_instruments_passes_data():
    wl = _FakeWatchlist()
    instruments = [{"symbol": "TSLA", "category": "US_STOCK", "sort": 1}]
    result = add_watchlist_instruments(_fake_sdk(wl), _config(), watchlist_id="wl-1", instruments=instruments)

    assert "Add Instruments" in result
    assert wl.calls[0] == ("add_instruments", {"watchlist_id": "wl-1", "instruments": instruments})


def test_remove_watchlist_instruments_passes_data():
    wl = _FakeWatchlist()
    instruments = [{"symbol": "TSLA", "category": "US_STOCK"}]
    result = remove_watchlist_instruments(_fake_sdk(wl), _config(), watchlist_id="wl-1", instruments=instruments)

    assert "Remove Instruments" in result
    assert wl.calls[0] == ("remove_instruments", {"watchlist_id": "wl-1", "instruments": instruments})


def test_update_watchlist_instruments_passes_data():
    wl = _FakeWatchlist()
    instruments = [{"symbol": "TSLA", "category": "US_STOCK", "sort": 3}]
    result = update_watchlist_instruments(_fake_sdk(wl), _config(), watchlist_id="wl-1", instruments=instruments)

    assert "Update Instruments" in result
    assert wl.calls[0] == ("update_instruments", {"watchlist_id": "wl-1", "instruments": instruments})
