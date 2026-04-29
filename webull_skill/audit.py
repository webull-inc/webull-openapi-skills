"""Audit logging for Webull OpenAPI Skill.

All audit events are emitted as single-line JSON to stderr (always) and
optionally to a rotating log file when ``WEBULL_AUDIT_LOG_FILE`` is configured.
"""

from __future__ import annotations

import copy
import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Any


# Fields whose values must never appear in any log output.
_CREDENTIAL_KEYS = frozenset({"app_key", "app_secret", "access_token"})

# Fields that are replaced with "***" in TOOL_CALL params.
_PRICE_SENSITIVE_KEYS = frozenset({"price", "stop_price"})


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        return record.getMessage()


class AuditLogger:
    """Structured audit logger for tool calls, order events and validation errors."""

    def __init__(self, audit_log_file: str | None = None) -> None:
        self._logger = logging.getLogger("webull_skill.audit")
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False

        # Remove any pre-existing handlers (important for tests / re-init).
        self._logger.handlers.clear()

        formatter = _JsonFormatter()

        # stderr handler — always enabled
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)
        self._logger.addHandler(stderr_handler)

        # Optional rotating file handler
        log_file = audit_log_file or os.environ.get("WEBULL_AUDIT_LOG_FILE")
        if log_file:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_tool_call(self, tool_name: str, params: dict[str, Any]) -> None:
        """Record a TOOL_CALL event with sanitised parameters."""
        sanitised = self._sanitize_params(params)
        self._emit({"event": "TOOL_CALL", "tool": tool_name, "params": sanitised})

    def log_order_attempt(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str,
        client_order_id: str,
        account_id: str,
    ) -> None:
        """Record an ORDER_ATTEMPT event."""
        self._emit(
            {
                "event": "ORDER_ATTEMPT",
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "order_type": order_type,
                "client_order_id": client_order_id,
                "account_id": account_id,
            }
        )

    def log_order_result(
        self, client_order_id: str, success: bool, response: dict[str, Any]
    ) -> None:
        """Record an ORDER_RESULT event."""
        safe_response = self._strip_credentials(response)
        self._emit(
            {
                "event": "ORDER_RESULT",
                "client_order_id": client_order_id,
                "success": success,
                "response": safe_response,
            }
        )

    def log_validation_error(
        self, tool_name: str, error: str, params: dict[str, Any]
    ) -> None:
        """Record a VALIDATION_ERROR event."""
        sanitised = self._sanitize_params(params)
        self._emit(
            {
                "event": "VALIDATION_ERROR",
                "tool": tool_name,
                "error": error,
                "params": sanitised,
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(self, payload: dict[str, Any]) -> None:
        """Add timestamp and write a single JSON line via the logger."""
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        self._logger.info(json.dumps(payload, default=str))

    @staticmethod
    def _sanitize_params(params: dict[str, Any]) -> dict[str, Any]:
        """Return a copy with price fields masked and credential keys removed."""
        result: dict[str, Any] = {}
        for key, value in params.items():
            if key in _CREDENTIAL_KEYS:
                continue
            if key in _PRICE_SENSITIVE_KEYS:
                result[key] = "***"
            else:
                result[key] = value
        return result

    @staticmethod
    def _strip_credentials(data: dict[str, Any]) -> dict[str, Any]:
        """Return a deep copy with all credential keys removed recursively."""
        cleaned = copy.deepcopy(data)
        AuditLogger._remove_keys_recursive(cleaned, _CREDENTIAL_KEYS)
        return cleaned

    @staticmethod
    def _remove_keys_recursive(obj: Any, keys: frozenset[str]) -> None:
        """Recursively remove keys from nested dicts/lists in-place."""
        if isinstance(obj, dict):
            for k in list(obj.keys()):
                if k in keys:
                    del obj[k]
                else:
                    AuditLogger._remove_keys_recursive(obj[k], keys)
        elif isinstance(obj, list):
            for item in obj:
                AuditLogger._remove_keys_recursive(item, keys)
