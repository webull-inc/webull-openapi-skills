"""Unit tests for option orders: leg-in / leg-out (API-1421) and JP single-leg options (API-1413)."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.trading.option_order import (
    _validate_jp_option_tax_type,
    place_option_single_order,
    preview_option_order,
)


class _FakeOrderV3:
    def __init__(self) -> None:
        self.place_calls: list[dict] = []
        self.preview_calls: list[dict] = []

    def preview_order(self, *, account_id: str, preview_orders: list[dict]) -> dict:
        self.preview_calls.append({
            "account_id": account_id,
            "preview_orders": preview_orders,
        })
        return {"estimated_amount": "500.00", "currency": "USD"}

    def place_order(self, *, account_id: str, new_orders: list[dict], **kwargs: object) -> dict:
        self.place_calls.append({
            "account_id": account_id,
            "new_orders": new_orders,
            **kwargs,
        })
        return {"client_order_id": "c1", "order_id": "o1"}


def _fake_sdk(
    *,
    account_id: str = "opt-1",
    account_class: str = "INDIVIDUAL_CASH",
    account_type: str = "CASH",
    region_id: str = "us",
) -> tuple[object, _FakeOrderV3]:
    order_v3 = _FakeOrderV3()
    account_v2 = SimpleNamespace(
        get_account_list=lambda: [
            {
                "account_id": account_id,
                "account_type": account_type,
                "account_class": account_class,
            }
        ]
    )
    trade = SimpleNamespace(account_v2=account_v2, order_v3=order_v3)
    return SimpleNamespace(region_id=region_id, trade=trade), order_v3


def _base_kwargs(**overrides: object) -> dict:
    kwargs: dict = {
        "symbol": "AAPL",
        "side": "BUY",
        "quantity": 1,
        "option_type": "CALL",
        "strike_price": 250.0,
        "expiration_date": "2026-06-19",
        "order_type": "LIMIT",
        "time_in_force": "DAY",
        "limit_price": 5.0,
        "account_id": "opt-1",
    }
    kwargs.update(overrides)
    return kwargs


def test_leg_in_forwards_all_fields_at_order_level():
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        leg_in_or_out="LEG_IN",
        position_id="FVIESMTK2IRC3FKKJSEE2U56SB",
        leg_in_strategy="VERTICAL",
        **_base_kwargs(),
    )

    assert "client_order_id: c1" in result
    order = order_v3.place_calls[0]["new_orders"][0]
    assert order["leg_in_or_out"] == "LEG_IN"
    assert order["position_id"] == "FVIESMTK2IRC3FKKJSEE2U56SB"
    assert order["leg_in_strategy"] == "VERTICAL"


def test_leg_out_forwards_fields_without_strategy():
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        leg_in_or_out="LEG_OUT",
        position_id="FVIESMTK2IRC3FKKJSEE2U56SB",
        **_base_kwargs(),
    )

    assert "client_order_id: c1" in result
    order = order_v3.place_calls[0]["new_orders"][0]
    assert order["leg_in_or_out"] == "LEG_OUT"
    assert order["position_id"] == "FVIESMTK2IRC3FKKJSEE2U56SB"
    assert "leg_in_strategy" not in order


def test_leg_in_requires_position_id():
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        leg_in_or_out="LEG_IN",
        leg_in_strategy="VERTICAL",
        **_base_kwargs(),
    )

    assert result == "Validation error: position_id is required when leg_in_or_out is specified"
    assert order_v3.place_calls == []


def test_leg_out_rejects_leg_in_strategy():
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        leg_in_or_out="LEG_OUT",
        position_id="FVIESMTK2IRC3FKKJSEE2U56SB",
        leg_in_strategy="VERTICAL",
        **_base_kwargs(),
    )

    assert result == "Validation error: leg_in_strategy is only applicable when leg_in_or_out is LEG_IN"
    assert order_v3.place_calls == []


def test_invalid_leg_in_or_out_value_rejected():
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        leg_in_or_out="LEG_SIDEWAYS",
        position_id="FVIESMTK2IRC3FKKJSEE2U56SB",
        **_base_kwargs(),
    )

    assert result.startswith("Validation error: Invalid leg_in_or_out")
    assert order_v3.place_calls == []


def test_leg_in_strategy_value_not_validated_client_side():
    """leg_in_strategy value is validated by the backend, not client-side -
    an unknown value is forwarded as-is."""
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        leg_in_or_out="LEG_IN",
        position_id="FVIESMTK2IRC3FKKJSEE2U56SB",
        leg_in_strategy="SOME_NEW_STRATEGY",
        **_base_kwargs(),
    )

    assert "client_order_id: c1" in result
    order = order_v3.place_calls[0]["new_orders"][0]
    assert order["leg_in_strategy"] == "SOME_NEW_STRATEGY"


def test_leg_in_strategy_without_leg_in_or_out_rejected():
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        leg_in_strategy="VERTICAL",
        **_base_kwargs(),
    )

    assert result == "Validation error: leg_in_strategy requires leg_in_or_out=LEG_IN"
    assert order_v3.place_calls == []


def test_leg_in_not_supported_in_hk():
    sdk, order_v3 = _fake_sdk(region_id="hk")
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="hk"),
        leg_in_or_out="LEG_IN",
        position_id="FVIESMTK2IRC3FKKJSEE2U56SB",
        **_base_kwargs(),
    )

    assert result.startswith("Validation error:")
    assert "option_leg_in_out" in result
    assert order_v3.place_calls == []


def test_normal_option_order_unaffected():
    sdk, order_v3 = _fake_sdk()
    result = place_option_single_order(
        sdk,
        SkillConfig(app_key="k", app_secret="s", region_id="us"),
        **_base_kwargs(),
    )

    assert "client_order_id: c1" in result
    order = order_v3.place_calls[0]["new_orders"][0]
    assert "leg_in_or_out" not in order
    assert "position_id" not in order
    assert "leg_in_strategy" not in order


# ---------------------------------------------------------------------------
# JP single-leg option orders (API-1413)
# ---------------------------------------------------------------------------

def _jp_config(region_id: str = "jp") -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id=region_id)


def _jp_option_sdk() -> tuple[object, _FakeOrderV3]:
    return _fake_sdk(
        account_class="INDIVIDUAL_US_OPTION",
        account_type="US_OPTION",
        region_id="jp",
    )


def test_jp_option_tax_type_missing_is_rejected():
    assert _validate_jp_option_tax_type(_jp_config(), None) == (
        "Validation error: account_tax_type is required for JP option orders"
    )
    assert _validate_jp_option_tax_type(_jp_config(), "") == (
        "Validation error: account_tax_type is required for JP option orders"
    )


def test_jp_option_tax_type_invalid_value_is_rejected():
    assert _validate_jp_option_tax_type(_jp_config(), "NISA") == (
        "Validation error: Invalid account_tax_type 'NISA'. Valid values: GENERAL, SPECIFIC"
    )


def test_jp_option_tax_type_valid_values_pass():
    assert _validate_jp_option_tax_type(_jp_config(), "GENERAL") is None
    assert _validate_jp_option_tax_type(_jp_config(), "SPECIFIC") is None


def test_jp_option_tax_type_not_checked_outside_jp():
    assert _validate_jp_option_tax_type(_jp_config("us"), None) is None


def test_jp_option_tax_type_region_check_is_case_insensitive():
    config = SimpleNamespace(region_id="JP")

    assert _validate_jp_option_tax_type(config, None) == (
        "Validation error: account_tax_type is required for JP option orders"
    )
    assert _validate_jp_option_tax_type(config, "GENERAL") is None


def test_jp_option_preview_forwards_position_intent_and_account_tax_type():
    sdk, order_v3 = _jp_option_sdk()
    kwargs = _base_kwargs()
    kwargs.pop("account_id")
    result = preview_option_order(
        sdk,
        _jp_config(),
        "opt-1",
        position_intent="BUY_TO_OPEN",
        account_tax_type="SPECIFIC",
        **kwargs,
    )

    assert "=== Order Preview ===" in result
    call = order_v3.preview_calls[0]
    assert call["account_id"] == "opt-1"
    order = call["preview_orders"][0]
    assert order["position_intent"] == "BUY_TO_OPEN"
    assert order["account_tax_type"] == "SPECIFIC"


def test_jp_option_place_requires_account_tax_type():
    sdk, order_v3 = _jp_option_sdk()
    result = place_option_single_order(sdk, _jp_config(), **_base_kwargs())

    assert result == "Validation error: account_tax_type is required for JP option orders"
    assert order_v3.place_calls == []


def test_jp_option_place_forwards_account_tax_type():
    sdk, order_v3 = _jp_option_sdk()
    result = place_option_single_order(
        sdk,
        _jp_config(),
        account_tax_type="GENERAL",
        **_base_kwargs(),
    )

    assert "client_order_id: c1" in result
    order = order_v3.place_calls[0]["new_orders"][0]
    assert order["account_tax_type"] == "GENERAL"
