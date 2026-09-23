"""Unit tests for CLI region gating."""

from __future__ import annotations

from argparse import Namespace

import pytest

from webull_skill.cli import _region_trading_error, dispatch_market_data, dispatch_trading
from webull_skill.config import SkillConfig


def test_dispatch_trading_blocks_unsupported_jp_action_before_sdk_import():
    # Single-leg option orders are supported in JP (API-1413); multi-leg
    # option strategies remain unsupported and are used here to exercise
    # the same pre-SDK-import region gate.
    result = dispatch_trading(
        Namespace(
            action="option-strategy-place",
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
    assert result.detail == "Validation error: Action 'option-strategy-place' is not supported in region 'jp'"


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


def _trading_args(action: str) -> Namespace:
    return Namespace(
        action=action,
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
    )


@pytest.mark.parametrize("action", ["option-place", "instrument-option-contracts"])
def test_dispatch_trading_blocks_option_actions_in_za(action):
    result = dispatch_trading(
        _trading_args(action),
        SkillConfig(app_key="k", app_secret="s", region_id="za"),
    )

    assert result.ok is False
    assert result.detail == f"Validation error: Action '{action}' is not supported in region 'za'"


def test_dispatch_market_data_blocks_option_snapshot_in_za():
    result = dispatch_market_data(
        Namespace(action="option-snapshot"),
        SkillConfig(app_key="k", app_secret="s", region_id="za"),
    )

    assert result.ok is False
    assert result.detail == "Validation error: Action 'option-snapshot' is not supported in region 'za'"


def test_jp_option_place_passes_region_gate():
    config = SkillConfig(app_key="k", app_secret="s", region_id="jp")

    assert _region_trading_error(config, "option-place", "US_OPTION") == ""
