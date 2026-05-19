"""Environment routing for Webull API endpoints.

Resolves OpenAPI host addresses based on environment (prod/uat)
and region (us/hk/jp).  Supports a priority chain:

    CLI direct > env var override > local config file override > default mapping

OAuth authentication is handled internally by the SDK's TokenManager,
so no separate OAuth endpoint configuration is needed.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Default config path: conf/env_routes.json relative to skill root
_DEFAULT_ROUTES_PATH = Path(__file__).resolve().parent.parent / "conf" / "env_routes.json"


# ---------------------------------------------------------------------------
# UAT endpoint types for SDK injection (quotes-api, events-api, etc.)
# The SDK's built-in endpoints.json only contains production endpoints.
# For UAT, we must register all three endpoint types via add_endpoint():
#   - api (DEFAULT): Used by TradeClient for trading operations
#   - quotes-api (QUOTES): Used by DataClient for market data
#   - events-api (EVENTS): Used by TradeEventsClient for streaming events
# ---------------------------------------------------------------------------
UAT_ENDPOINTS: dict[str, dict[str, str]] = {
    "us": {
        "api": "us-openapi-alb.uat.webullbroker.com",
        "quotes-api": "us-openapi-quotes-api.uat.webullbroker.com",
        "events-api": "us-openapi-events.uat.webullbroker.com",
    },
    "hk": {
        "api": "api.sandbox.webull.hk",
        "quotes-api": "data-api.sandbox.webull.hk",
        "events-api": "events-api.sandbox.webull.hk",
    },
    "jp": {
        "api": "jp-openapi-alb.uat.webullbroker.com",
        "quotes-api": "data-api.uat.webullbroker.com",
        "events-api": "jp-openapi-events.uat.webullbroker.com",
    },
    "sg": {
        "api": "sg-api.uat.webullbroker.com",
        "quotes-api": "data-api.uat.webullbroker.com",
        "events-api": "sg-events-api.uat.webullbroker.com",
    },
}


# ---------------------------------------------------------------------------
# Default OpenAPI host mapping
# ---------------------------------------------------------------------------
DEFAULT_HOSTS: dict[tuple[str, str], str] = {
    ("prod", "us"): "api.webull.com",
    ("uat", "us"): "us-openapi-alb.uat.webullbroker.com",
    ("prod", "hk"): "api.webull.hk",
    ("uat", "hk"): "api.sandbox.webull.hk",
    ("uat", "jp"): "jp-openapi-alb.uat.webullbroker.com",
    ("prod", "sg"): "api.webull.com.sg",
    ("uat", "sg"): "sg-api.uat.webullbroker.com",
}


class EnvRouter:
    """Resolve API endpoints by environment and region.

    Resolution priority (highest wins):
        1. CLI direct value (passed as *cli_override* parameter)
        2. Environment variable ``WEBULL_OPENAPI_HOST_{ENV}_{REGION}``
        3. Local config file override (``conf/env_routes.json``)
        4. Built-in default mapping
    """

    def __init__(self, routes_path: str | None = None) -> None:
        self._routes_path = Path(routes_path) if routes_path else _DEFAULT_ROUTES_PATH
        self._file_overrides: dict[str, Any] | None = None

    def resolve(
        self,
        env: str,
        region_id: str,
        cli_override: str = "",
    ) -> str:
        """Return the OpenAPI host for *env* / *region_id*.

        Parameters
        ----------
        env:
            Environment identifier (``prod`` or ``uat``).
        region_id:
            Region identifier (``us``, ``hk``, or ``jp``).
        cli_override:
            If non-empty, returned directly (highest priority).
        """
        if cli_override:
            return cli_override

        env_key = f"WEBULL_OPENAPI_HOST_{env.upper()}_{region_id.upper()}"
        env_val = os.environ.get(env_key, "").strip()
        if env_val:
            return env_val

        file_val = self._file_host(env, region_id)
        if file_val:
            return file_val

        return self._default_host(env, region_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _file_host(self, env: str, region_id: str) -> str:
        """Look up a host value from the optional local config file."""
        overrides = self._load_file_overrides()
        if overrides is None:
            return ""
        route_key = f"{env.lower()}/{region_id.lower()}"
        return str(overrides.get(route_key, "")).strip()

    @staticmethod
    def _default_host(env: str, region_id: str) -> str:
        """Look up a host value from the built-in default mapping."""
        key = (env.lower(), region_id.lower())
        host = DEFAULT_HOSTS.get(key)
        if host is None:
            raise ValueError(
                f"Unknown env/region combination: env={env!r}, region_id={region_id!r}. "
                f"Valid combinations: {sorted(DEFAULT_HOSTS.keys())}"
            )
        return host

    def _load_file_overrides(self) -> dict[str, Any] | None:
        """Load and cache the optional local config file.

        Expected format::

            {
                "prod/us": "api.webull.com",
                "uat/us": "us-openapi-alb.uat.webullbroker.com"
            }

        Returns ``None`` when the file does not exist (not an error).
        """
        if self._file_overrides is not None:
            return self._file_overrides

        if not self._routes_path.exists():
            self._file_overrides = {}
            return None

        try:
            text = self._routes_path.read_text(encoding="utf-8")
            data = json.loads(text)
        except (OSError, json.JSONDecodeError):
            self._file_overrides = {}
            return None

        if not isinstance(data, dict):
            self._file_overrides = {}
            return None

        self._file_overrides = data
        return data
