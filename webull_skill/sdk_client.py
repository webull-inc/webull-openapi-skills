"""Webull SDK client wrapper — manages ApiClient/TradeClient/DataClient lifecycle.

This is the only layer that touches the Webull SDK directly.
Token persistence is handled by the SDK's built-in TokenManager/TokenStorage.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING

from webull.core.client import ApiClient
from webull.core.common.api_type import DEFAULT, QUOTES, EVENTS
from webull.core.exception.exceptions import ClientException, ServerException
from webull.data.data_client import DataClient
from webull.trade.trade_client import TradeClient

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig

from webull_skill.env_router import UAT_ENDPOINTS

# Mapping from config keys to SDK api_type constants
_API_TYPE_MAP = {
    "api": DEFAULT,
    "quotes-api": QUOTES,
    "events-api": EVENTS,
}

# Region-specific 2FA documentation links
_2FA_GUIDE_LINKS: dict[str, str] = {
    "hk": "https://developer.webull.hk/apis/docs/authentication/token",
    "jp": "https://developer.webull.co.jp/api-doc/authentication/token/",
    "my": "https://developer.webull.com.my/apis/docs/authentication/token",
    "sg": "https://developer.webull.com.sg/apis/docs/authentication/token",
    "th": "https://developer.webull.co.th/apis/docs/authentication/token",
    "uk": "https://developer.webull-uk.com/apis/docs/authentication/token",
    "us": "https://developer.webull.com/apis/docs/authentication/token",
}


def _2fa_guide_link(region_id: str) -> str:
    """Return the 2FA guide URL for the given region, defaulting to US."""
    return _2FA_GUIDE_LINKS.get(region_id, _2FA_GUIDE_LINKS["us"])


class TwoFactorAuthRequiredError(Exception):
    """Raised when 2FA verification is required but user hasn't approved yet."""

    def __init__(self, region_id: str, environment: str) -> None:
        self.region_id = region_id
        self.environment = environment
        guide = _2fa_guide_link(region_id)
        super().__init__(
            "2FA Authentication Required\n"
            "===========================\n\n"
            "Your account requires Two-Factor Authentication (2FA).\n\n"
            "Steps to resolve:\n"
            "  1. Run:  webull-skill auth\n"
            "  2. Approve the 2FA request in your Webull app\n"
            "  3. Re-run your command\n\n"
            f"2FA Guide: {guide}\n"
            f"Region: {region_id.upper()}  |  Environment: {environment.upper()}"
        )


class DeviceNotRegisteredError(Exception):
    """Raised when no device is registered for 2FA verification."""

    def __init__(self, region_id: str, environment: str) -> None:
        self.region_id = region_id
        self.environment = environment
        guide = _2fa_guide_link(region_id)
        super().__init__(
            "Device Not Registered\n"
            "=====================\n\n"
            "No device is registered for 2FA verification.\n\n"
            "Steps to resolve:\n"
            "  1. Download the latest Webull mobile app\n"
            "  2. Log in with the account linked to your API credentials\n"
            "  3. Complete device registration\n"
            "  4. Run:  webull-skill auth\n\n"
            f"2FA Guide: {guide}\n"
            f"Region: {region_id.upper()}  |  Environment: {environment.upper()}"
        )


def _configure_uat_endpoints(api_client: ApiClient, cfg: "SkillConfig") -> None:
    """Inject UAT endpoints when running in UAT environment."""
    if cfg.environment != "uat":
        return
    region_cfg = UAT_ENDPOINTS.get(cfg.region_id)
    if not region_cfg:
        return
    for key, api_type in _API_TYPE_MAP.items():
        endpoint = region_cfg.get(key)
        if endpoint:
            api_client.add_endpoint(cfg.region_id, endpoint, api_type)


def _configure_logging(api_client: ApiClient) -> None:
    """Redirect SDK logging to stderr with configurable level."""
    log_level_str = os.environ.get("WEBULL_LOG_LEVEL", "WARNING").upper()
    log_level = getattr(logging, log_level_str, logging.WARNING)
    api_client.set_stream_logger(log_level=log_level, stream=sys.stderr)


def _create_clients(
    api_client: ApiClient, cfg: "SkillConfig",
) -> tuple[TradeClient, DataClient]:
    """Create TradeClient and DataClient, translating auth errors."""
    try:
        trade = TradeClient(api_client)
        data = DataClient(api_client)
    except ServerException as e:
        if e.error_code == "NO_AVAILABLE_DEVICE":
            raise DeviceNotRegisteredError(cfg.region_id, cfg.environment) from e
        raise
    except ClientException as e:
        if "ERROR_INIT_TOKEN" in str(e) or "ERROR_CHECK_TOKEN" in str(e):
            raise TwoFactorAuthRequiredError(cfg.region_id, cfg.environment) from e
        raise
    return trade, data


class SDKClient:
    """Webull SDK client wrapper.

    Encapsulates the full ApiClient / TradeClient / DataClient lifecycle.
    Token management is handled by the SDK's built-in TokenManager.
    """

    # Non-interactive mode: fail fast if 2FA required
    DEFAULT_TOKEN_CHECK_DURATION = 10   # seconds (vs SDK default 300)
    DEFAULT_TOKEN_CHECK_INTERVAL = 2    # seconds (vs SDK default 5)

    # Interactive mode (auth command): wait for user to approve 2FA
    INTERACTIVE_TOKEN_CHECK_DURATION = 300
    INTERACTIVE_TOKEN_CHECK_INTERVAL = 5

    def __init__(self, config: "SkillConfig") -> None:
        self._config = config
        self._api_client: ApiClient | None = None
        self._trade_client: TradeClient | None = None
        self._data_client: DataClient | None = None

    def initialize(self, interactive: bool = False) -> None:
        """Create and wire up all SDK clients.

        Args:
            interactive: If True, use longer timeout for interactive 2FA auth.
                        If False (default), fail fast if 2FA is required.

        Steps:
        1. Set client source identifier so SDK can distinguish skill calls
        2. Create ApiClient with token check timeout
        3. Set token_dir if configured
        4. For UAT: inject all three endpoint types (DEFAULT, QUOTES, EVENTS)
        5. Configure SDK logging
        6. Create TradeClient and DataClient (triggers token init)
        """
        cfg = self._config

        # 1. Set client source identifier; the SDK attaches this as the
        #    x-webull-client-source header on all HTTP requests.
        #    setdefault preserves any value already set in the environment.
        os.environ.setdefault("WEBULL_CLIENT_SOURCE", "skill")

        # Token check timeout based on mode
        if interactive:
            duration = self.INTERACTIVE_TOKEN_CHECK_DURATION
            interval = self.INTERACTIVE_TOKEN_CHECK_INTERVAL
        else:
            duration = self.DEFAULT_TOKEN_CHECK_DURATION
            interval = self.DEFAULT_TOKEN_CHECK_INTERVAL

        # 2. Core API client
        api_client = ApiClient(
            cfg.app_key,
            cfg.app_secret,
            cfg.region_id,
            token_check_duration_seconds=duration,
            token_check_interval_seconds=interval,
        )

        # 3. Token persistence directory
        if cfg.token_dir:
            api_client.set_token_dir(cfg.token_dir)

        # 4. UAT endpoint injection
        _configure_uat_endpoints(api_client, cfg)

        # 5. SDK logging configuration
        _configure_logging(api_client)

        # 6. Trade / Data clients
        self._api_client = api_client
        self._trade_client, self._data_client = _create_clients(api_client, cfg)

    @property
    def trade(self) -> TradeClient:
        """Return the initialized TradeClient."""
        if self._trade_client is None:
            raise RuntimeError("SDK not initialized - call initialize() first")
        return self._trade_client

    @property
    def data(self) -> DataClient:
        """Return the initialized DataClient."""
        if self._data_client is None:
            raise RuntimeError("SDK not initialized - call initialize() first")
        return self._data_client

    @property
    def region_id(self) -> str:
        """Return the configured region id."""
        return self._config.region_id.lower()
