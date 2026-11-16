"""Unit tests for result.py."""

import json
import pytest

from webull_skill.result import OperationResult, success, failure


class TestOperationResult:
    """Tests for OperationResult dataclass."""

    def test_success_result_basic(self):
        r = success(payload={"price": 100})
        assert r.ok is True
        assert r.payload == {"price": 100}

    def test_failure_result_basic(self):
        r = failure("something went wrong", status_code=400)
        assert r.ok is False
        assert r.detail == "something went wrong"
        assert r.status_code == 400

    def test_failure_requires_detail(self):
        with pytest.raises(ValueError, match="detail must be non-empty"):
            OperationResult(ok=False, detail="")

    def test_failure_requires_detail_missing(self):
        with pytest.raises(ValueError, match="detail must be non-empty"):
            OperationResult(ok=False)

    def test_success_allows_empty_detail(self):
        r = OperationResult(ok=True, detail="")
        assert r.detail == ""

    def test_to_dict_contains_all_fields(self):
        r = success(payload={"data": 1}, config_label="us/uat", action="snapshot")
        d = r.to_dict()
        assert set(d.keys()) == {
            "ok", "status_code", "detail", "payload", "config_label", "action", "trade_outcome"
        }

    def test_to_json_valid(self):
        r = success(payload={"symbol": "AAPL"}, action="stock-snapshot")
        j = r.to_json()
        parsed = json.loads(j)
        assert parsed["ok"] is True
        assert parsed["payload"]["symbol"] == "AAPL"

    def test_to_json_ensure_ascii_false(self):
        r = success(payload={"name": "test-data"})
        j = r.to_json()
        assert "test-data" in j

    def test_to_json_indent(self):
        r = success(payload=None)
        j = r.to_json()
        # indent=2 means multi-line output
        assert "\n" in j

    def test_trade_outcome_field(self):
        r = success(payload={}, trade_outcome="success", action="place-order")
        assert r.trade_outcome == "success"
        d = r.to_dict()
        assert d["trade_outcome"] == "success"

    def test_failure_factory_kwargs(self):
        r = failure("err", config_label="us/uat", action="cancel")
        assert r.config_label == "us/uat"
        assert r.action == "cancel"

    def test_config_label_field(self):
        r = success(payload={}, config_label="hk/prod")
        assert r.config_label == "hk/prod"
        d = r.to_dict()
        assert d["config_label"] == "hk/prod"


class TestDefaultCategory:
    """default_category infers the market category from the action name."""

    @pytest.mark.parametrize(
        "action",
        [
            "instrument-option-contracts",
            "option-snapshot",
            "option-bars",
            "option-tick",
            "option-place",
        ],
    )
    def test_option_actions_default_to_us_option(self, action):
        from webull_skill.result import default_category

        assert default_category(action) == "US_OPTION"

    @pytest.mark.parametrize(
        "action, expected",
        [
            ("instrument-futures-list", "US_FUTURES"),
            ("futures-bars", "US_FUTURES"),
            ("instrument-crypto", "US_CRYPTO"),
            ("crypto-bars", "US_CRYPTO"),
            ("instrument-event-events", "US_EVENT"),
            ("event-bars", "US_EVENT"),
            ("instrument-stock", "US_STOCK"),
            ("stock-snapshot", "US_STOCK"),
            ("balance", "US_STOCK"),
        ],
    )
    def test_other_actions_keep_their_default(self, action, expected):
        from webull_skill.result import default_category

        assert default_category(action) == expected
