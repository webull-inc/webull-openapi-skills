"""Structured operation result for all Skill operations.

Includes shared helpers (_extract, _call) used by both TradingOps
and MarketDataOps to convert SDK responses into OperationResult.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OperationResult:
    """Standardized return structure for all operations.

    Invariant: when ok is False, detail MUST be non-empty.
    """

    ok: bool
    status_code: int | None = None
    detail: str = ""
    payload: Any = None
    config_label: str = ""
    action: str = ""
    trade_outcome: str | None = None  # success/failure/pending/partial_fill/unknown

    def __post_init__(self) -> None:
        if not self.ok and not self.detail:
            raise ValueError("detail must be non-empty when ok is False")

    def to_dict(self) -> dict:
        """Convert to a serializable dictionary."""
        return {
            "ok": self.ok,
            "status_code": self.status_code,
            "detail": self.detail,
            "payload": self.payload,
            "config_label": self.config_label,
            "action": self.action,
            "trade_outcome": self.trade_outcome,
        }

    def to_json(self) -> str:
        """Serialize to JSON string (ensure_ascii=False, indent=2)."""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


def success(payload: Any = None, **kwargs: Any) -> OperationResult:
    """Build a success result."""
    return OperationResult(ok=True, payload=payload, **kwargs)


def failure(detail: str, status_code: int | None = None, **kwargs: Any) -> OperationResult:
    """Build a failure result."""
    return OperationResult(ok=False, detail=detail, status_code=status_code, **kwargs)


# ---------------------------------------------------------------------------
# Shared SDK-response helpers
# ---------------------------------------------------------------------------

def _extract(response: Any) -> OperationResult:
    """Turn an SDK response (requests.Response) into an OperationResult."""
    code = getattr(response, "status_code", None)
    try:
        payload = response.json()
    except Exception:
        payload = None
    if code == 200:
        return success(payload=payload, status_code=code)
    detail = ""
    if isinstance(payload, dict):
        detail = (
            payload.get("message")
            or payload.get("msg")
            or payload.get("error_code")
            or ""
        )
    return failure(
        detail=detail or f"API error (HTTP {code})",
        status_code=code,
        payload=payload,
    )


def _call(fn: Any, *args: Any, **kwargs: Any) -> OperationResult:
    """Execute an SDK call, returning an OperationResult."""
    try:
        response = fn(*args, **kwargs)
        return _extract(response)
    except Exception as exc:
        code = getattr(exc, "status_code", None) or getattr(exc, "http_status", None)
        msg = getattr(exc, "message", None) or str(exc)
        return failure(detail=msg, status_code=code)


def default_category(action: str) -> str:
    """Infer the default category from an action name prefix."""
    a = action.lower()
    if a.startswith("futures") or a.startswith("instrument-futures"):
        return "US_FUTURES"
    if a.startswith("crypto") or a.startswith("instrument-crypto"):
        return "US_CRYPTO"
    if a.startswith("event") or a.startswith("instrument-event"):
        return "US_EVENT"
    return "US_STOCK"
