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
            series_symbol="",
            order_json="",
            order_file="",
            client_order_id="",
        ),
        SkillConfig(app_key="k", app_secret="s", region_id="jp"),
    )

    assert result.ok is False
    assert result.detail == "Validation error: Action 'option-strategy-place' is not supported in region 'jp'"


def test_status_error_accepts_documented_values_per_action():
    from webull_skill.cli import _status_error

    assert _status_error("instrument-stock", "OC") == ""
    assert _status_error("instrument-crypto", "NT") == ""
    assert _status_error("instrument-futures-list", "CO") == ""
    assert _status_error("instrument-event-events", "ACTIVE") == ""
    assert _status_error("instrument-event-events", "INACTIVE") == ""
    assert _status_error("instrument-option-contracts", "LISTING") == ""
    assert _status_error("instrument-option-contracts", "DELISTING") == ""
    # An empty status means "not provided" and is always fine.
    assert _status_error("balance", "") == ""


def test_status_error_rejects_values_from_another_endpoint():
    from webull_skill.cli import _status_error

    assert "Valid values: OC, CO, NT" in _status_error("instrument-stock", "LISTING")
    assert "Valid values: ACTIVE, INACTIVE" in _status_error("instrument-event-events", "OC")
    assert "Valid values: LISTING, DELISTING" in _status_error("instrument-option-contracts", "ACTIVE")


def test_status_error_rejects_actions_without_a_status_filter():
    from webull_skill.cli import _status_error

    assert "not supported by action 'balance'" in _status_error("balance", "OC")


def test_dispatch_trading_rejects_invalid_status_before_sdk_import():
    result = dispatch_trading(
        Namespace(
            action="instrument-event-events",
            symbol="",
            symbols="",
            category="",
            account_id="",
            instrument_id="",
            series_symbol="ECONOMICS",
            order_json="",
            order_file="",
            client_order_id="",
            status="OC",
        ),
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
    )

    assert result.ok is False
    assert result.detail == (
        "Validation error: Invalid --status 'OC' for 'instrument-event-events'. "
        "Valid values: ACTIVE, INACTIVE"
    )


def test_dispatch_trading_blocks_position_detail_outside_jp():
    result = dispatch_trading(
        Namespace(
            action="position-detail",
            symbol="",
            symbols="",
            category="",
            account_id="acct-1",
            instrument_id="9001",
            series_symbol="",
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


def _fake_dispatch(monkeypatch, region="us"):
    """Patch SDKClient and return the MagicMock standing in for the SDK."""
    from unittest.mock import MagicMock

    sdk = MagicMock()
    sdk.data.instrument.list_event_series.return_value = {}
    sdk.data.instrument.list_event_instruments.return_value = {}
    sdk.data.instrument.get_futures_products.return_value = {}
    monkeypatch.setattr("webull_skill.sdk_client.SDKClient", lambda config: sdk)
    return sdk, SkillConfig(app_key="k", app_secret="s", region_id=region)


def _trading_ns(action, **overrides):
    values = dict(
        action=action, symbol="", symbols="", code="", status="", category="",
        sub_category="", account_id="", instrument_id="", series_symbol="",
        event_symbol="", expiration_date_after="", product_class_id="",
        order_json="", order_file="", client_order_id="", pagination_key="",
    )
    values.update(overrides)
    return Namespace(**values)


def test_event_list_passes_filters(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_trading(
        _trading_ns(
            "instrument-event-list", series_symbol="ECON", event_symbol="KXFED",
            symbols="A,B", expiration_date_after="2026-12-01",
        ),
        config,
    )
    kwargs = sdk.data.instrument.list_event_instruments.call_args.kwargs
    assert kwargs["series_symbol"] == "ECON"
    assert kwargs["event_symbol"] == "KXFED"
    assert kwargs["symbols"] == ["A", "B"]
    assert kwargs["expiration_date_after"] == "2026-12-01"


def test_event_list_omits_unset_filters(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_trading(_trading_ns("instrument-event-list", series_symbol="ECON"), config)
    kwargs = sdk.data.instrument.list_event_instruments.call_args.kwargs
    assert set(kwargs) == {"series_symbol"}


def test_event_series_passes_symbols(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_trading(_trading_ns("instrument-event-series", symbols="S1,S2"), config)
    assert sdk.data.instrument.list_event_series.call_args.kwargs["symbols"] == ["S1", "S2"]


def test_futures_products_passes_product_class_id(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_trading(_trading_ns("instrument-futures-products", product_class_id="42"), config)
    assert sdk.data.instrument.get_futures_products.call_args.kwargs["product_class_id"] == "42"


def test_futures_products_omits_unset_product_class_id(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_trading(_trading_ns("instrument-futures-products"), config)
    assert "product_class_id" not in sdk.data.instrument.get_futures_products.call_args.kwargs


def _market_ns(action, **overrides):
    values = dict(
        action=action, symbol="AAPL", symbols="", category="", timespan="D", count=200,
        depth=None, trading_sessions="", real_time_required=False,
        extend_hour_required=False, overnight_required=False, start_time=None, end_time=None,
    )
    values.update(overrides)
    return Namespace(**values)


def test_stock_quotes_passes_depth(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_market_data(_market_ns("stock-quotes", depth=5), config)
    assert sdk.data.market_data.get_quotes.call_args.kwargs["depth"] == 5


def test_stock_quotes_omits_depth_when_unset(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_market_data(_market_ns("stock-quotes"), config)
    assert "depth" not in sdk.data.market_data.get_quotes.call_args.kwargs


@pytest.mark.parametrize("action", ["stock-bars", "stock-batch-bars"])
def test_stock_bars_pass_real_time_required(monkeypatch, action):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_market_data(_market_ns(action, real_time_required=True, timespan="M1"), config)
    kwargs = sdk.data.market_data.get_batch_history_bar.call_args.kwargs
    assert kwargs["real_time_required"] is True


def test_status_flag_is_case_insensitive():
    from webull_skill.cli import build_parser

    args = build_parser().parse_args(["trading", "--action", "instrument-stock", "--status", "oc"])
    assert args.status == "OC"


def test_event_series_omits_category_when_not_given(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_trading(_trading_ns("instrument-event-series"), config)
    assert "category" not in sdk.data.instrument.list_event_series.call_args.kwargs


def test_event_series_passes_event_category(monkeypatch):
    sdk, config = _fake_dispatch(monkeypatch)
    dispatch_trading(_trading_ns("instrument-event-series", category="ECONOMICS"), config)
    assert sdk.data.instrument.list_event_series.call_args.kwargs["category"] == "ECONOMICS"
