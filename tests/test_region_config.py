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
