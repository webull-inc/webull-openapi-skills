"""Unit tests for market_data.community."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.formatters import (
    format_community_hot_stocks,
    format_community_post_list,
)
from webull_skill.market_data.community import (
    create_comment,
    create_post,
    get_post,
    list_hot_stocks,
    list_my_posts,
    list_posts_by_symbol,
)


class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeCommunity:
    def __init__(self) -> None:
        self.calls: dict[str, list] = {
            "create_post": [],
            "create_comment": [],
            "list_hot_stocks": [],
            "list_posts_by_symbol": [],
            "get_post": [],
            "list_my_posts": [],
        }

    def create_post(self, text, symbol=None, category=None):
        self.calls["create_post"].append((text, symbol, category))
        return _FakeResponse({"post_id": "995005758239301632"})

    def create_comment(self, post_id, text):
        self.calls["create_comment"].append((post_id, text))
        return _FakeResponse({"comment_id": "123456"})

    def list_hot_stocks(self):
        self.calls["list_hot_stocks"].append(())
        return _FakeResponse({"data": [
            {"rank": 1, "symbol": "NVDA", "category": "US_STOCK"},
            {"rank": 2, "symbol": "AAPL", "category": "US_STOCK"},
        ]})

    def list_posts_by_symbol(self, symbol, category, keyword=None, pagination_key=None):
        self.calls["list_posts_by_symbol"].append((symbol, category, keyword, pagination_key))
        return _FakeResponse({
            "data": [{"post_id": "1", "text": "hello", "publish_time": "2026-10-20",
                      "thumbs": 3, "comments": 1}],
            "pagination_key": "cursor-abc",
        })

    def get_post(self, post_id):
        self.calls["get_post"].append((post_id,))
        return _FakeResponse({
            "post_id": post_id, "text": "great earnings", "publish_time": "2026-10-20",
            "thumbs": 10, "comments": 4,
            "tickers": [{"symbol": "NVDA", "category": "US_STOCK"}],
        })

    def list_my_posts(self, pagination_key=None):
        self.calls["list_my_posts"].append((pagination_key,))
        return _FakeResponse({"data": [
            {"post_id": "7", "text": "mine", "publish_time": "2026-10-20",
             "thumbs": 0, "comments": 0}]})


def _fake_sdk(community: _FakeCommunity) -> object:
    data = SimpleNamespace(community=community)
    return SimpleNamespace(data=data, region_id="us")


def _config() -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id="us")


def test_create_post_passes_symbol_and_category():
    community = _FakeCommunity()
    result = create_post(_fake_sdk(community), _config(), text="hi", symbol="NVDA", category="US_STOCK")
    assert "Post ID: 995005758239301632" in result
    assert community.calls["create_post"][0] == ("hi", "NVDA", "US_STOCK")


def test_create_comment_formats_comment_id():
    community = _FakeCommunity()
    result = create_comment(_fake_sdk(community), _config(), post_id="995", text="nice")
    assert "Comment ID: 123456" in result
    assert community.calls["create_comment"][0] == ("995", "nice")


def test_list_hot_stocks_formats_ranking():
    community = _FakeCommunity()
    result = list_hot_stocks(_fake_sdk(community), _config())
    assert "Community Hot Stocks" in result
    assert "#1  NVDA  (US_STOCK)" in result
    assert "#2  AAPL  (US_STOCK)" in result


def test_list_posts_by_symbol_formats_and_passes_args():
    community = _FakeCommunity()
    result = list_posts_by_symbol(
        _fake_sdk(community), _config(),
        symbol="NVDA", category="US_STOCK", keyword="earnings", pagination_key="k1",
    )
    assert "Community Posts by Symbol" in result
    assert "Post ID: 1" in result
    assert "pagination_key=cursor-abc" in result
    assert community.calls["list_posts_by_symbol"][0] == ("NVDA", "US_STOCK", "earnings", "k1")


def test_get_post_formats_detail_with_tickers():
    community = _FakeCommunity()
    result = get_post(_fake_sdk(community), _config(), post_id="995")
    assert "Community Post Detail" in result
    assert "Post ID: 995" in result
    assert "NVDA (US_STOCK)" in result


def test_list_my_posts_formats_and_passes_pagination_key():
    community = _FakeCommunity()
    result = list_my_posts(_fake_sdk(community), _config(), pagination_key="cursor-9")
    assert "Community My Posts" in result
    assert "Post ID: 7" in result
    assert community.calls["list_my_posts"][0] == ("cursor-9",)


def test_empty_hot_stocks_returns_no_data():
    community = _FakeCommunity()
    community.list_hot_stocks = lambda: _FakeResponse({"data": []})
    result = list_hot_stocks(_fake_sdk(community), _config())
    assert "No data available" in result


# ---------------------------------------------------------------------------
# dispatch 层回归：community-create-post 的 symbol/category 成对校验
# （API-1987：纯文本发帖此前被 default_category 填默认 US_STOCK 导致误拒）
# ---------------------------------------------------------------------------

def _make_args(**overrides):
    """构造 dispatch_market_data 所需的最小 argparse.Namespace。"""
    base = dict(
        action="community-create-post",
        category="", symbol="", symbols="", text="",
        post_id="", keyword="", pagination_key="",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _patch_dispatch(monkeypatch):
    """把 dispatch_market_data 里的 SDKClient 与 create_post 替换成可观测的 fake。"""
    import webull_skill.cli as cli
    import webull_skill.sdk_client as sdk_mod
    import webull_skill.market_data.community as comm

    class _FakeSDK:
        def __init__(self, *a, **k):
            pass

        def initialize(self):
            pass

    calls = {}

    def _fake_create_post(sdk, config, text, symbol=None, category=None):
        calls["args"] = {"text": text, "symbol": symbol, "category": category}
        return "=== Community ===\n  Post ID: 1"

    monkeypatch.setattr(sdk_mod, "SDKClient", _FakeSDK)
    monkeypatch.setattr(comm, "create_post", _fake_create_post)
    return cli, calls


def test_dispatch_pure_text_post_not_rejected(monkeypatch):
    cli, calls = _patch_dispatch(monkeypatch)
    args = _make_args(text="hello world")  # 无 symbol / category

    result = cli.dispatch_market_data(args, _config())

    # 不应被成对校验拦截；create_post 被调用，且 category 为 None（纯文本）
    assert calls.get("args") is not None, f"create_post 未被调用，疑似被误拒: {result}"
    assert calls["args"]["symbol"] is None
    assert calls["args"]["category"] is None


def test_dispatch_symbol_without_category_rejected(monkeypatch):
    cli, calls = _patch_dispatch(monkeypatch)
    args = _make_args(text="hello", symbol="NVDA")  # 只有 symbol

    result = cli.dispatch_market_data(args, _config())

    assert calls.get("args") is None, "只传 symbol 不应调用 create_post"
    assert getattr(result, "ok", None) is False
    assert "provided together" in result.detail


# ---------------------------------------------------------------------------
# Text length validation (local, before hitting the SDK)
# ---------------------------------------------------------------------------

from webull_skill.market_data.community import (  # noqa: E402
    MAX_COMMENT_TEXT_LENGTH,
    MAX_POST_TEXT_LENGTH,
)


def test_create_post_rejects_empty_text():
    comm = _FakeCommunity()
    sdk = _fake_sdk(comm)
    result = create_post(sdk, _config(), "")
    assert "text must not be empty" in result
    assert comm.calls["create_post"] == []  # SDK not called


def test_create_post_rejects_text_over_limit():
    comm = _FakeCommunity()
    sdk = _fake_sdk(comm)
    result = create_post(sdk, _config(), "x" * (MAX_POST_TEXT_LENGTH + 1))
    assert f"must not exceed {MAX_POST_TEXT_LENGTH}" in result
    assert comm.calls["create_post"] == []  # SDK not called


def test_create_post_accepts_text_at_limit():
    comm = _FakeCommunity()
    sdk = _fake_sdk(comm)
    result = create_post(sdk, _config(), "x" * MAX_POST_TEXT_LENGTH)
    assert "Post ID" in result
    assert len(comm.calls["create_post"]) == 1  # boundary is inclusive


def test_create_comment_rejects_empty_text():
    comm = _FakeCommunity()
    sdk = _fake_sdk(comm)
    result = create_comment(sdk, _config(), "post-1", "")
    assert "text must not be empty" in result
    assert comm.calls["create_comment"] == []


def test_create_comment_rejects_text_over_limit():
    comm = _FakeCommunity()
    sdk = _fake_sdk(comm)
    result = create_comment(sdk, _config(), "post-1", "x" * (MAX_COMMENT_TEXT_LENGTH + 1))
    assert f"must not exceed {MAX_COMMENT_TEXT_LENGTH}" in result
    assert comm.calls["create_comment"] == []


def test_create_comment_accepts_text_at_limit():
    comm = _FakeCommunity()
    sdk = _fake_sdk(comm)
    result = create_comment(sdk, _config(), "post-1", "x" * MAX_COMMENT_TEXT_LENGTH)
    assert "Comment ID" in result
    assert len(comm.calls["create_comment"]) == 1


# ---------------------------------------------------------------------------
# Formatter malformed-payload handling
# ---------------------------------------------------------------------------


def test_community_list_formatters_return_no_data_for_non_list_payloads():
    for payload in ({"data": 1}, {"data": {"post_id": "1"}}):
        assert "No data available" in format_community_hot_stocks(payload)
        assert "No data available" in format_community_post_list(payload)


def test_create_post_rejects_symbol_without_category_for_direct_call():
    community = _FakeCommunity()

    result = create_post(_fake_sdk(community), _config(), text="hi", symbol="NVDA")

    assert "symbol and category must be provided together" in result
    assert community.calls["create_post"] == []


def test_create_post_rejects_category_without_symbol_for_direct_call():
    community = _FakeCommunity()

    result = create_post(
        _fake_sdk(community), _config(), text="hi", category="US_STOCK"
    )

    assert "symbol and category must be provided together" in result
    assert community.calls["create_post"] == []


def test_create_post_normalizes_empty_ticker_association_for_direct_call():
    community = _FakeCommunity()

    result = create_post(
        _fake_sdk(community), _config(), text="hi", symbol="", category=""
    )

    assert "Post ID" in result
    assert community.calls["create_post"] == [("hi", None, None)]



def test_community_post_list_keeps_cursor_for_empty_page():
    result = format_community_post_list(
        {"data": [], "pagination_key": "next-page"}
    )

    assert "No data available" in result
    assert "pagination_key=next-page" in result
