"""Unit tests for JP order validation rules."""

from __future__ import annotations

import pytest

from webull_skill.config import SkillConfig
from webull_skill.errors import ValidationError
from webull_skill.guards import validate_stock_order


def _jp_config() -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id="jp")


def _base_params(**overrides: object) -> dict[str, object]:
    params: dict[str, object] = {
        "symbol": "AAPL",
        "side": "BUY",
        "order_type": "LIMIT",
        "time_in_force": "DAY",
        "quantity": 1,
        "entrust_type": "QTY",
        "market": "US",
        "limit_price": 100,
    }
    params.update(overrides)
    return params


def test_jp_allows_us_stop_loss_limit_and_gtc():
    validate_stock_order(
        _base_params(
            order_type="STOP_LOSS_LIMIT",
            time_in_force="GTC",
            market="US",
            limit_price=101,
            stop_price=99,
        ),
        _jp_config(),
    )


def test_jp_allows_all_day_trading_session():
    validate_stock_order(
        _base_params(trading_session="ALL_DAY"),
        _jp_config(),
    )


def test_jp_us_market_rejects_gtd():
    with pytest.raises(ValidationError, match="Invalid time_in_force 'GTD' for US market"):
        validate_stock_order(
            _base_params(time_in_force="GTD", market="US"),
            _jp_config(),
        )


def test_jp_market_rejects_stop_orders():
    with pytest.raises(ValidationError, match="Invalid order_type 'STOP_LOSS' for JP market"):
        validate_stock_order(
            _base_params(order_type="STOP_LOSS", market="JP", limit_price=None, stop_price=99),
            _jp_config(),
        )


def test_jp_market_rejects_non_day_tif():
    with pytest.raises(ValidationError, match="Invalid time_in_force 'GTC' for JP market"):
        validate_stock_order(
            _base_params(market="JP", time_in_force="GTC"),
            _jp_config(),
        )


def test_jp_region_rejects_hk_market():
    with pytest.raises(ValidationError, match="Invalid market 'HK' for region 'jp'"):
        validate_stock_order(
            _base_params(market="HK"),
            _jp_config(),
        )
