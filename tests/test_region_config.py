"""Unit tests for region_config.py."""

from webull_skill.region_config import SUPPORTED_REGIONS, get_region_config


def test_jp_region_is_supported():
    assert "jp" in SUPPORTED_REGIONS
    assert get_region_config("JP").region_id == "jp"


def test_jp_region_market_specific_rules():
    config = get_region_config("jp")

    assert config.valid_order_markets == frozenset({"US", "JP"})
    assert config.valid_market_categories == frozenset({"US_STOCK", "US_ETF"})
    assert config.valid_trading_sessions == frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"})
    assert config.valid_order_types_by_market == {
        "JP": frozenset({"LIMIT", "MARKET"}),
        "US": frozenset({"LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"}),
    }
    assert config.valid_time_in_force_by_market == {
        "JP": frozenset({"DAY"}),
        "US": frozenset({"DAY", "GTC"}),
    }




def test_th_region_is_supported():
    assert "th" in SUPPORTED_REGIONS
    assert get_region_config("TH").region_id == "th"
    assert get_region_config("th").region_id == "th"


def test_th_region_config():
    config = get_region_config("th")

    assert config.valid_order_markets == frozenset({"US"})
    assert config.valid_market_categories == frozenset({"US_STOCK", "US_ETF"})
    assert config.valid_order_types == frozenset({"LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"})
    assert config.valid_time_in_force == frozenset({"DAY", "GTC"})
    assert config.valid_trading_sessions == frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"})
    assert config.supports_futures is False


def test_th_region_supports_single_leg_options():
    config = get_region_config("th")

    # Single-leg US options are enabled for TH (API-1413): option account
    # classes mirror the stock account classes; multi-leg strategies stay off.
    assert config.asset_type_account_classes is not None
    assert config.asset_type_account_classes.get("option") == frozenset({"INDIVIDUAL_CASH"})
    assert config.valid_option_strategies == frozenset({"SINGLE"})
    assert config.supports_option_strategies is False


def test_my_region_is_supported():
    assert "my" in SUPPORTED_REGIONS
    assert get_region_config("MY").region_id == "my"
    assert get_region_config("my").region_id == "my"


def test_my_region_config():
    config = get_region_config("my")

    assert config.valid_order_markets == frozenset({"US"})
    assert config.valid_market_categories == frozenset({"US_STOCK", "US_ETF"})
    assert config.valid_order_types == frozenset({"LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"})
    assert config.valid_time_in_force == frozenset({"DAY", "GTC"})
    assert config.valid_trading_sessions == frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"})
    assert config.supports_futures is False
    assert config.supports_crypto is False
    assert config.supports_event_contracts is False
    assert config.supports_combo_orders is False
    assert config.supports_option_strategies is False
    assert config.supports_algo_orders is False


def test_uk_region_is_supported():
    assert "uk" in SUPPORTED_REGIONS
    assert get_region_config("UK").region_id == "uk"
    assert get_region_config("uk").region_id == "uk"


def test_uk_region_config():
    config = get_region_config("uk")

    assert config.valid_order_markets == frozenset({"US"})
    assert config.valid_market_categories == frozenset({"US_STOCK", "US_ETF"})
    assert config.valid_order_types == frozenset({"LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"})
    assert config.valid_time_in_force == frozenset({"DAY", "GTC"})
    assert config.valid_trading_sessions == frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"})
    assert config.supports_futures is False
    assert config.supports_crypto is False
    assert config.supports_event_contracts is False
    assert config.supports_combo_orders is False
    assert config.supports_option_strategies is False
    assert config.supports_algo_orders is False




def test_za_region_is_supported():
    assert "za" in SUPPORTED_REGIONS
    assert get_region_config("ZA").region_id == "za"
    assert get_region_config("za").region_id == "za"


def test_za_region_config():
    config = get_region_config("za")

    assert config.valid_order_markets == frozenset({"US"})
    assert config.valid_market_categories == frozenset({"US_STOCK", "US_ETF"})
    assert config.valid_order_types == frozenset({"LIMIT", "MARKET", "STOP_LOSS", "STOP_LOSS_LIMIT"})
    assert config.valid_time_in_force == frozenset({"DAY", "GTC"})
    assert config.valid_trading_sessions == frozenset({"ALL", "ALL_DAY", "CORE", "NIGHT"})
    assert config.supports_futures is False
    assert config.supports_crypto is False
    assert config.supports_event_contracts is False
    assert config.supports_combo_orders is False
    assert config.supports_option_strategies is False
    assert config.supports_algo_orders is False


def test_mx_and_br_accept_individual_margin_account_class():
    # MX/BR margin accounts may report account_class INDIVIDUAL_MARGIN.
    for region_id in ("mx", "br"):
        classes = get_region_config(region_id).asset_type_account_classes
        assert classes is not None
        assert "INDIVIDUAL_MARGIN" in classes["stock"]
        assert "INDIVIDUAL_MARGIN" in classes["option"]


def test_za_has_no_option_account_classes():
    classes = get_region_config("za").asset_type_account_classes
    assert classes is not None
    assert "option" not in classes
