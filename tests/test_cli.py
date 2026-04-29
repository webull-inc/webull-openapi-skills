"""Unit tests for CLI region gating."""

from __future__ import annotations

from argparse import Namespace

from webull_skill.cli import dispatch_market_data, dispatch_trading
from webull_skill.config import SkillConfig


def test_dispatch_trading_blocks_unsupported_jp_action_before_sdk_import():
    result = dispatch_trading(
        Namespace(
            action="option-place",
            symbol="",
            symbols="",
            category="",
            account_id="",
            instrument_id="",
            last_id="",
            code="",
            series_symbol="",
            page_size=500,
            order_json="",
            order_file="",
            client_order_id="",
        ),
        SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert result.ok is False
    assert result.detail == "Validation error: Action 'option-place' is not supported in region 'jp'"


def test_dispatch_trading_blocks_position_detail_outside_jp():
    result = dispatch_trading(
        Namespace(
            action="position-detail",
            symbol="",
            symbols="",
            category="",
            account_id="acct-1",
            instrument_id="9001",
            last_id="",
            code="",
            series_symbol="",
            page_size=20,
            order_json="",
            order_file="",
            client_order_id="",
        ),
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
    )

    assert result.ok is False
    assert result.detail == "Validation error: Action 'position-detail' is only supported in region 'jp'"


def test_dispatch_market_data_blocks_non_stock_actions_for_jp():
    result = dispatch_market_data(
        Namespace(
            action="futures-snapshot",
            symbol="",
            symbols="",
            category="",
            timespan="D",
            count=200,
            depth=1,
            trading_sessions="",
            real_time_required=False,
            extend_hour_required=False,
            overnight_required=False,
        ),
        SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert result.ok is False
    assert result.detail == "Validation error: Market data action 'futures-snapshot' is not supported in region 'jp'"
