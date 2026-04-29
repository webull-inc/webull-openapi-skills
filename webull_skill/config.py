"""Configuration management for Webull OpenAPI Skill."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from webull_skill.errors import ConfigError


@dataclass
class SkillConfig:
    """Configuration loaded from environment variables / .env file."""
    app_key: str
    app_secret: str
    region_id: str = "us"
    environment: str = "uat"
    max_order_notional_usd: float = 10_000.0
    max_order_notional_hkd: float = 80_000.0
    max_order_notional_cnh: float = 70_000.0
    max_order_notional_jpy: float = 1_500_000.0
    max_order_quantity: float = 1_000.0
    symbol_whitelist: list[str] | None = None
    audit_log_file: str | None = None
    token_dir: str | None = None

    def get_max_notional_for_market(self, market: str | None) -> tuple[float, str]:
        """Get max notional limit and currency for a specific market."""
        if market == "HK":
            return (self.max_order_notional_hkd, "HKD")
        elif market == "CN":
            return (self.max_order_notional_cnh, "CNH")
        elif market == "JP":
            return (self.max_order_notional_jpy, "JPY")
        else:
            return (self.max_order_notional_usd, "USD")


def _parse_whitelist(raw: str | None) -> list[str] | None:
    """Parse comma-separated whitelist string into a list, or None if empty."""
    if not raw or not raw.strip():
        return None
    items = [s.strip() for s in raw.split(",") if s.strip()]
    return items if items else None


def _parse_float(raw: str | None, default: float) -> float:
    """Parse a string to float, returning default on None or invalid input."""
    if raw is None:
        return default
    try:
        return float(raw)
    except (ValueError, TypeError):
        return default


# Default token directory: conf/ at project root (sibling of webull_skill/)
# Can be overridden via WEBULL_CONFIG_DIR environment variable.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_TOKEN_DIR = str(_PROJECT_ROOT / "conf")


def _resolve_config_dir() -> Path:
    """Resolve the config directory.

    Priority:
    1. WEBULL_CONFIG_DIR environment variable (user-specified path)
    2. Project root (default — sibling of webull_skill/)
    """
    custom = os.environ.get("WEBULL_CONFIG_DIR", "").strip()
    if custom:
        return Path(custom).expanduser().resolve()
    return _PROJECT_ROOT


def load_config(env_file: str | None = None) -> SkillConfig:
    """Load configuration from environment variables / .env file.

    Parameters
    ----------
    env_file:
        Optional explicit path to a .env file. When provided the file is
        loaded before reading os.environ so that file values act as defaults
        that real env-vars can override (python-dotenv default behaviour).

    .env lookup order (when env_file is not provided):
    1. $WEBULL_CONFIG_DIR/.env  (if WEBULL_CONFIG_DIR is set)
    2. <project_root>/.env      (default)
    3. Current working directory .env (last resort)
    """
    if env_file is not None:
        load_dotenv(env_file, override=False)
    else:
        config_dir = _resolve_config_dir()
        env_path = config_dir / ".env"
        if env_path.exists():
            load_dotenv(str(env_path), override=False)
        else:
            load_dotenv(override=False)

    # Token dir: WEBULL_TOKEN_DIR > WEBULL_CONFIG_DIR/conf/ > project_root/conf/
    token_dir = (
        os.environ.get("WEBULL_TOKEN_DIR")
        or str(_resolve_config_dir() / "conf")
    )

    return SkillConfig(
        app_key=os.environ.get("WEBULL_APP_KEY", ""),
        app_secret=os.environ.get("WEBULL_APP_SECRET", ""),
        region_id=os.environ.get("WEBULL_REGION_ID", "us"),
        environment=os.environ.get("WEBULL_ENVIRONMENT", "uat"),
        max_order_notional_usd=_parse_float(os.environ.get("WEBULL_MAX_ORDER_NOTIONAL_USD"), 10_000.0),
        max_order_notional_hkd=_parse_float(os.environ.get("WEBULL_MAX_ORDER_NOTIONAL_HKD"), 80_000.0),
        max_order_notional_cnh=_parse_float(os.environ.get("WEBULL_MAX_ORDER_NOTIONAL_CNH"), 70_000.0),
        max_order_notional_jpy=_parse_float(os.environ.get("WEBULL_MAX_ORDER_NOTIONAL_JPY"), 1_500_000.0),
        max_order_quantity=_parse_float(os.environ.get("WEBULL_MAX_ORDER_QUANTITY"), 1_000.0),
        symbol_whitelist=_parse_whitelist(os.environ.get("WEBULL_SYMBOL_WHITELIST")),
        audit_log_file=os.environ.get("WEBULL_AUDIT_LOG_FILE") or None,
        token_dir=token_dir,
    )


def validate_config(config: SkillConfig) -> None:
    """Validate that required credentials are present.

    Raises
    ------
    ConfigError
        If ``app_key`` or ``app_secret`` is empty / missing, or region is invalid.
    """
    if not config.app_key:
        raise ConfigError(
            "WEBULL_APP_KEY is required but not set. "
            "Provide it via environment variable or .env file."
        )
    if not config.app_secret:
        raise ConfigError(
            "WEBULL_APP_SECRET is required but not set. "
            "Provide it via environment variable or .env file."
        )

    # Validate region configuration
    from webull_skill.region_config import get_region_config

    try:
        get_region_config(config.region_id)  # raises UnsupportedRegionError if invalid
    except Exception as e:
        raise ConfigError(str(e)) from e
