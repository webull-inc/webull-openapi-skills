"""Unit tests for config module."""

from __future__ import annotations

import os
import pytest
from pathlib import Path

from webull_skill.config import (
    SkillConfig,
    ConfigError,
    load_config,
    validate_config,
    _parse_whitelist,
    _parse_float,
)


class TestSkillConfig:
    def test_defaults(self):
        c = SkillConfig(app_key="k", app_secret="s")
        assert c.region_id == "us"
        assert c.environment == "uat"
        assert c.max_order_notional_usd == 10_000.0
        assert c.max_order_notional_hkd == 80_000.0
        assert c.max_order_notional_cnh == 70_000.0
        assert c.max_order_notional_jpy == 1_500_000.0
        assert c.max_order_quantity == 1_000.0
        assert c.symbol_whitelist is None
        assert c.token_dir is None

    def test_get_max_notional_us(self):
        c = SkillConfig(app_key="k", app_secret="s")
        val, currency = c.get_max_notional_for_market("US")
        assert val == 10_000.0
        assert currency == "USD"

    def test_get_max_notional_hk(self):
        c = SkillConfig(app_key="k", app_secret="s", max_order_notional_hkd=50_000.0)
        val, currency = c.get_max_notional_for_market("HK")
        assert val == 50_000.0
        assert currency == "HKD"

    def test_get_max_notional_cn(self):
        c = SkillConfig(app_key="k", app_secret="s", max_order_notional_cnh=30_000.0)
        val, currency = c.get_max_notional_for_market("CN")
        assert val == 30_000.0
        assert currency == "CNH"

    def test_get_max_notional_jp(self):
        c = SkillConfig(app_key="k", app_secret="s", max_order_notional_jpy=1_200_000.0)
        val, currency = c.get_max_notional_for_market("JP")
        assert val == 1_200_000.0
        assert currency == "JPY"

    def test_get_max_notional_default(self):
        c = SkillConfig(app_key="k", app_secret="s")
        val, currency = c.get_max_notional_for_market(None)
        assert val == 10_000.0
        assert currency == "USD"


class TestParseWhitelist:
    def test_none(self):
        assert _parse_whitelist(None) is None

    def test_empty(self):
        assert _parse_whitelist("") is None

    def test_whitespace(self):
        assert _parse_whitelist("   ") is None

    def test_single(self):
        assert _parse_whitelist("AAPL") == ["AAPL"]

    def test_multiple(self):
        assert _parse_whitelist("AAPL, MSFT, GOOGL") == ["AAPL", "MSFT", "GOOGL"]

    def test_trailing_comma(self):
        assert _parse_whitelist("AAPL,MSFT,") == ["AAPL", "MSFT"]


class TestParseFloat:
    def test_none(self):
        assert _parse_float(None, 5.0) == 5.0

    def test_valid(self):
        assert _parse_float("123.45", 0.0) == 123.45

    def test_invalid(self):
        assert _parse_float("abc", 99.0) == 99.0

    def test_empty(self):
        assert _parse_float("", 7.0) == 7.0


class TestLoadConfig:
    def test_from_env_file(self, tmp_path: Path, monkeypatch):
        # Clear any existing env vars
        for key in ["WEBULL_APP_KEY", "WEBULL_APP_SECRET", "WEBULL_REGION_ID",
                     "WEBULL_ENVIRONMENT", "WEBULL_SYMBOL_WHITELIST",
                     "WEBULL_MAX_ORDER_NOTIONAL_JPY", "WEBULL_TOKEN_DIR"]:
            monkeypatch.delenv(key, raising=False)

        env_file = tmp_path / ".env"
        env_file.write_text(
            "WEBULL_APP_KEY=test_key\n"
            "WEBULL_APP_SECRET=test_secret\n"
            "WEBULL_REGION_ID=hk\n"
            "WEBULL_ENVIRONMENT=prod\n"
            "WEBULL_MAX_ORDER_NOTIONAL_JPY=1200000\n",
            encoding="utf-8",
        )
        config = load_config(str(env_file))
        assert config.app_key == "test_key"
        assert config.app_secret == "test_secret"
        assert config.region_id == "hk"
        assert config.environment == "prod"
        assert config.max_order_notional_jpy == 1_200_000.0

    def test_env_var_override(self, tmp_path: Path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "WEBULL_APP_KEY=file_key\n"
            "WEBULL_APP_SECRET=file_secret\n",
            encoding="utf-8",
        )
        # Real env var should take priority (load_dotenv override=False)
        monkeypatch.setenv("WEBULL_APP_KEY", "env_key")
        config = load_config(str(env_file))
        assert config.app_key == "env_key"

    def test_defaults_when_empty(self, tmp_path: Path, monkeypatch):
        for key in ["WEBULL_APP_KEY", "WEBULL_APP_SECRET", "WEBULL_REGION_ID",
                     "WEBULL_ENVIRONMENT", "WEBULL_MAX_ORDER_NOTIONAL_USD",
                     "WEBULL_MAX_ORDER_NOTIONAL_HKD", "WEBULL_MAX_ORDER_NOTIONAL_CNH",
                     "WEBULL_MAX_ORDER_NOTIONAL_JPY",
                     "WEBULL_MAX_ORDER_QUANTITY", "WEBULL_SYMBOL_WHITELIST",
                     "WEBULL_TOKEN_DIR"]:
            monkeypatch.delenv(key, raising=False)

        env_file = tmp_path / ".env"
        env_file.write_text("", encoding="utf-8")
        config = load_config(str(env_file))
        assert config.app_key == ""
        assert config.app_secret == ""
        assert config.region_id == "us"
        assert config.environment == "uat"
        assert config.max_order_notional_usd == 10_000.0
        assert config.max_order_notional_hkd == 80_000.0
        assert config.max_order_notional_cnh == 70_000.0
        assert config.max_order_notional_jpy == 1_500_000.0
        assert config.max_order_quantity == 1_000.0
        assert config.symbol_whitelist is None
        assert config.token_dir is not None
        assert config.token_dir.endswith("/conf")

    def test_whitelist_parsing(self, tmp_path: Path, monkeypatch):
        for key in ["WEBULL_APP_KEY", "WEBULL_APP_SECRET", "WEBULL_REGION_ID",
                     "WEBULL_ENVIRONMENT", "WEBULL_TOKEN_DIR"]:
            monkeypatch.delenv(key, raising=False)

        env_file = tmp_path / ".env"
        env_file.write_text(
            "WEBULL_APP_KEY=k\n"
            "WEBULL_APP_SECRET=s\n"
            "WEBULL_SYMBOL_WHITELIST=AAPL,MSFT,GOOGL\n",
            encoding="utf-8",
        )
        config = load_config(str(env_file))
        assert config.symbol_whitelist == ["AAPL", "MSFT", "GOOGL"]


class TestValidateConfig:
    def test_valid(self):
        config = SkillConfig(app_key="k", app_secret="s")
        validate_config(config)  # should not raise

    def test_valid_jp_region(self):
        config = SkillConfig(app_key="k", app_secret="s", region_id="jp")
        validate_config(config)  # should not raise

    def test_missing_app_key(self):
        config = SkillConfig(app_key="", app_secret="s")
        with pytest.raises(ConfigError, match="WEBULL_APP_KEY"):
            validate_config(config)

    def test_missing_app_secret(self):
        config = SkillConfig(app_key="k", app_secret="")
        with pytest.raises(ConfigError, match="WEBULL_APP_SECRET"):
            validate_config(config)

    def test_both_missing(self):
        config = SkillConfig(app_key="", app_secret="")
        with pytest.raises(ConfigError, match="WEBULL_APP_KEY"):
            validate_config(config)
