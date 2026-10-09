"""Unit tests for market_data.news."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.market_data.news import (
    get_news_detail,
    get_stock_news,
    search_news,
)


class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeNews:
    """Records calls to the US-only news methods."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def get_news_search(self, *args: object, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_news_search", args, kwargs))
        return _FakeResponse({
            "keyword": "Starlink",
            "data": [{
                "news_id": "15716519902127104",
                "title": "Musk calls spectrum deal 'an earthquake'",
                "source": "Benzinga",
                "publish_time": "2026-10-09T05:02:20.000+0000",
                "sentiment": "NEUTRAL",
            }],
        })

    def get_news_detail(self, *args: object, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_news_detail", args, kwargs))
        return _FakeResponse({
            "news_id": "15716519902127104",
            "title": "Musk calls spectrum deal 'an earthquake'",
            "source": "Benzinga",
            "content": "<p>full article body</p>",
        })

    def get_stock_news(self, *args: object, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_stock_news", args, kwargs))
        return _FakeResponse({
            "symbol": "TSLA",
            "pagination_key": "1791348877000",
            "data": [{"news_id": "15716519902127104", "title": "some title"}],
        })


def _fake_sdk(news: _FakeNews) -> object:
    data = SimpleNamespace(news=news)
    return SimpleNamespace(data=data, region_id="us")


def _config() -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id="us")


def test_search_news():
    news = _FakeNews()
    sdk = _fake_sdk(news)
    result = search_news(sdk, _config(), "Starlink")

    assert "=== News Keyword Search ===" in result
    assert "Musk calls spectrum deal" in result
    assert news.calls == [("get_news_search", ("Starlink", None, None, None), {})]


def test_get_news_detail():
    news = _FakeNews()
    sdk = _fake_sdk(news)
    result = get_news_detail(sdk, _config(), "15716519902127104")

    assert "=== News Detail ===" in result
    assert "full article body" in result
    assert news.calls == [("get_news_detail", ("15716519902127104",), {})]


def test_get_stock_news():
    news = _FakeNews()
    sdk = _fake_sdk(news)
    result = get_stock_news(sdk, _config(), "TSLA")

    assert "=== Stock News List ===" in result
    assert "Next pagination_key: 1791348877000" in result
    assert news.calls == [("get_stock_news", ("TSLA",),
                           {"category": "US_STOCK", "sentiment": None, "pagination_key": None})]


# ---------------------------------------------------------------------------
# Keyword length validation (local, before hitting the SDK)
# ---------------------------------------------------------------------------

from webull_skill.market_data.news import MAX_NEWS_KEYWORD_LENGTH  # noqa: E402


def test_search_news_rejects_empty_keyword():
    news = _FakeNews()
    sdk = _fake_sdk(news)
    result = search_news(sdk, _config(), "")
    assert "keyword must not be empty" in result
    assert news.calls == []  # SDK not called


def test_search_news_rejects_keyword_over_limit():
    news = _FakeNews()
    sdk = _fake_sdk(news)
    result = search_news(sdk, _config(), "x" * (MAX_NEWS_KEYWORD_LENGTH + 1))
    assert f"must not exceed {MAX_NEWS_KEYWORD_LENGTH}" in result
    assert news.calls == []  # SDK not called


def test_search_news_accepts_keyword_at_limit():
    news = _FakeNews()
    sdk = _fake_sdk(news)
    result = search_news(sdk, _config(), "x" * MAX_NEWS_KEYWORD_LENGTH)
    assert "News Keyword Search" in result
    assert len(news.calls) == 1  # boundary is inclusive



def test_get_stock_news_rejects_invalid_sentiment():
    news = _FakeNews()
    sdk = _fake_sdk(news)

    result = get_stock_news(sdk, _config(), "TSLA", sentiment="mixed")

    assert "sentiment must be one of POSITIVE, NEGATIVE, NEUTRAL" in result
    assert news.calls == []
