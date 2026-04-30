"""Risk engine for pre-trade order validation.

Validates orders against SkillConfig constraints (from .env) before
they reach the Webull API. Checks: quantity, notional value, and
symbol whitelist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from webull_skill.config import SkillConfig


@dataclass
class RiskViolation:
    """A single risk-policy violation."""
    field: str
    message: str
    order_index: int | None = None


@dataclass
class RiskCheckResult:
    """Aggregated result of all risk checks."""
    allowed: bool
    violations: list[RiskViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class RiskEngine:
    """Order validation engine driven by SkillConfig."""

    def __init__(self, config: "SkillConfig") -> None:
        self._config = config

    def check_orders(self, orders: list[dict]) -> RiskCheckResult:
        """Run all risk checks. Returns fail-closed result."""
        violations: list[RiskViolation] = []

        for idx, order in enumerate(orders):
            self._check_quantity(order, idx, violations)
            self._check_notional(order, idx, violations)
            self._check_symbol_whitelist(order, idx, violations)

        return RiskCheckResult(
            allowed=len(violations) == 0,
            violations=violations,
        )

    def _check_quantity(self, order: dict, idx: int, violations: list[RiskViolation]) -> None:
        quantity = _to_float(order.get("quantity"))
        if quantity is not None and quantity > self._config.max_order_quantity:
            violations.append(RiskViolation(
                field="quantity",
                message=f"Quantity {quantity} exceeds max {self._config.max_order_quantity}",
                order_index=idx,
            ))

    def _check_notional(self, order: dict, idx: int, violations: list[RiskViolation]) -> None:
        quantity = _to_float(order.get("quantity"))
        price = _to_float(order.get("limit_price"))
        if quantity is None or price is None:
            return
        notional = quantity * price
        market = order.get("market", "US")
        max_notional, currency = self._config.get_max_notional_for_market(market)
        if notional > max_notional:
            violations.append(RiskViolation(
                field="notional",
                message=f"Notional {notional:.2f} {currency} exceeds max {max_notional:.2f} {currency}",
                order_index=idx,
            ))

    def _check_symbol_whitelist(self, order: dict, idx: int, violations: list[RiskViolation]) -> None:
        whitelist = self._config.symbol_whitelist
        if not whitelist:
            return
        symbol = order.get("symbol", "")
        if symbol and symbol not in whitelist:
            violations.append(RiskViolation(
                field="symbol",
                message=f"'{symbol}' not in whitelist: {whitelist}",
                order_index=idx,
            ))


def _to_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
