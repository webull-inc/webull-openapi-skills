"""Unit tests for market_data.fundamentals and screener extended functions."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.config import SkillConfig
from webull_skill.formatters import (
    _format_generic_list,
    format_capital_flow,
    format_industry_comparison,
    format_sec_filings,
    format_earnings_calendar,
    format_dividend_calendar,
    format_financials_indicators,
    format_financials_income,
    format_financials_cashflow,
    format_financials_balance_sheet,
    format_financials_alert,
    format_fund_brief,
    format_fund_allocation,
    format_fund_holdings,
    format_fund_performance,
    format_fund_rating,
    format_fund_net_value,
    format_fund_dividends,
    format_fund_splits,
    format_fund_files,
    format_market_sectors,
    format_market_sectors_detail,
    format_high_dividend,
    format_52whl,
)
from webull_skill.market_data.fundamentals import (
    get_capital_flow,
    get_earnings_calendar,
    get_fund_brief,
)
from webull_skill.market_data.screener import (
    get_market_sectors,
    get_high_dividend,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeFundamentals:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def get_capital_flow(self, **kwargs):
        self.calls.append(("capital_flow", kwargs))
        return _FakeResponse({
            "data": [
                {"date": "2026-06-20", "super_large_inflow": "100", "large_inflow": "50",
                 "medium_inflow": "30", "small_inflow": "20"}
            ]
        })

    def get_earnings_calendar(self, **kwargs):
        self.calls.append(("earnings_calendar", kwargs))
        return _FakeResponse({
            "data": [
                {"fiscal_year": "2026", "fiscal_period": "Q2",
                 "expected_publish_date": "2026-07-25", "currency": "USD",
                 "eps_est": "1.50", "eps_actual": None,
                 "rev_est": "90000000000", "rev_actual": None}
            ]
        })

    def get_fund_brief(self, **kwargs):
        self.calls.append(("fund_brief", kwargs))
        return _FakeResponse({
            "symbol": "QQQ", "name": "Invesco QQQ Trust",
            "inception_date": "1999-03-10", "expense_ratio": "0.20",
        })


class _FakeScreenerExt:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def get_market_sectors(self, **kwargs):
        self.calls.append(("market_sectors", kwargs))
        return _FakeResponse({
            "data": [
                {"sector_id": "10001", "sector_name": "Technology",
                 "change_ratio": "0.025", "market_value": "15000000000000"}
            ]
        })

    def get_high_dividend(self, **kwargs):
        self.calls.append(("high_dividend", kwargs))
        return _FakeResponse({
            "data": [
                {"symbol": "T", "name": "AT&T Inc", "yield": "6.5",
                 "market_value": "150000000000"}
            ]
        })

    # Stubs needed by screener module (it imports all from the same class)
    def get_gainers_losers(self, **kwargs):
        return _FakeResponse({"data": []})

    def get_most_active(self, **kwargs):
        return _FakeResponse({"data": []})

    def get_market_sectors_detail(self, **kwargs):
        return _FakeResponse({"data": []})

    def get_52whl(self, **kwargs):
        return _FakeResponse({"data": []})


def _fake_sdk_fundamentals(fundamentals):
    data = SimpleNamespace(fundamentals=fundamentals)
    return SimpleNamespace(data=data, region_id="us")


def _fake_sdk_screener(screener):
    data = SimpleNamespace(screener=screener)
    return SimpleNamespace(data=data, region_id="us")


def _config() -> SkillConfig:
    return SkillConfig(app_key="k", app_secret="s", region_id="us")


# ---------------------------------------------------------------------------
# _format_generic_list tests
# ---------------------------------------------------------------------------

class TestFormatGenericList:
    def test_empty_data(self):
        assert "No data available" in _format_generic_list(None, "Test")
        assert "No data available" in _format_generic_list([], "Test")
        assert "No data available" in _format_generic_list({}, "Test")

    def test_list_input(self):
        data = [{"key1": "val1", "key2": "val2"}]
        result = _format_generic_list(data, "My Title")
        assert "=== My Title ===" in result
        assert "key1: val1" in result
        assert "key2: val2" in result

    def test_dict_wrapper_with_data_key(self):
        data = {"data": [{"a": 1, "b": 2}]}
        result = _format_generic_list(data, "Wrapped")
        assert "=== Wrapped ===" in result
        assert "a: 1" in result
        assert "b: 2" in result

    def test_custom_key_candidates(self):
        data = {"sectors": [{"name": "Tech", "value": "100"}]}
        result = _format_generic_list(data, "Sectors", key_candidates=("sectors",))
        assert "name: Tech" in result
        assert "value: 100" in result

    def test_none_values_filtered(self):
        data = [{"visible": "yes", "hidden": None}]
        result = _format_generic_list(data, "Filter")
        assert "visible: yes" in result
        assert "hidden" not in result

    def test_dict_fallback_to_single_item(self):
        data = {"solo_key": "solo_val"}
        result = _format_generic_list(data, "Solo")
        assert "solo_key: solo_val" in result


# ---------------------------------------------------------------------------
# Formatter tests: fundamentals
# ---------------------------------------------------------------------------

class TestFundamentalsFormatters:
    def test_format_capital_flow(self):
        data = {"data": [{"date": "2026-06-20", "inflow": "100", "outflow": None}]}
        result = format_capital_flow(data)
        assert "=== Capital Flow ===" in result
        assert "date: 2026-06-20" in result
        assert "inflow: 100" in result
        assert "outflow" not in result  # None filtered

    def test_format_industry_comparison(self):
        data = {
            "type": "EPS_TTM", "industry_name": "Semiconductors",
            "stocks": [{"symbol": "NVDA", "name": "Nvidia", "rank": "1", "value": "5.2"}]
        }
        result = format_industry_comparison(data)
        assert "=== Industry Comparison ===" in result
        assert "Industry:        Semiconductors" in result
        assert "Sort By:         EPS_TTM" in result
        assert "Symbol:          NVDA" in result

    def test_format_sec_filings(self):
        data = {"filings": [{"title": "10-K", "publish_date": "2026-01-15", "url": "https://sec.gov/a"}]}
        result = format_sec_filings(data)
        assert "=== SEC Filings ===" in result
        assert "Title:           10-K" in result
        assert "URL:             https://sec.gov/a" in result

    def test_format_earnings_calendar(self):
        data = [{"fiscal_year": "2026", "fiscal_period": "Q2",
                 "expected_publish_date": "2026-07-25", "currency": "USD",
                 "eps_est": "1.50", "eps_actual": "1.60",
                 "rev_est": "90B", "rev_actual": "92B"}]
        result = format_earnings_calendar(data)
        assert "=== Earnings Calendar ===" in result
        assert "Fiscal Year:     2026" in result
        assert "EPS Actual:      1.60" in result

    def test_format_dividend_calendar(self):
        data = [{"ex_dividend_date": "2026-08-01", "record_date": "2026-08-02",
                 "pay_date": "2026-08-15", "amount": "0.25", "currency": "USD"}]
        result = format_dividend_calendar(data)
        assert "=== Dividend Calendar ===" in result
        assert "Amount:          0.25" in result

    def test_format_financials_indicators_values_format(self):
        data = {"currency": "USD", "values": {
            "EPS": [{"fiscal_year": "2026", "fiscal_period": "1", "value": "3.5"}]
        }}
        result = format_financials_indicators(data)
        assert "=== Financials Indicators ===" in result
        assert "Currency:        USD" in result
        assert "FY2026 Q1: 3.5" in result

    def test_format_financials_income(self):
        data = [{"fiscal_year": "2025", "revenue": "100000"}]
        result = format_financials_income(data)
        assert "=== Financials Income Statement ===" in result
        assert "revenue: 100000" in result

    def test_format_financials_cashflow(self):
        data = [{"operating_cash_flow": "50000"}]
        result = format_financials_cashflow(data)
        assert "=== Financials Cashflow Statement ===" in result

    def test_format_financials_balance_sheet(self):
        data = [{"total_assets": "200000"}]
        result = format_financials_balance_sheet(data)
        assert "=== Financials Balance Sheet ===" in result

    def test_format_financials_alert_dict(self):
        data = {"fiscal_year": "2026", "fiscal_period": "Q3", "start_date": "2026-07-01",
                "end_date": "2026-09-30", "currency": "USD",
                "eps_est": "2.0", "eps_ly": "1.8", "rev_est": "95B", "rev_ly": "88B"}
        result = format_financials_alert(data)
        assert "=== Financials Alert ===" in result
        assert "EPS Estimate:    2.0" in result

    def test_format_fund_brief(self):
        data = {"symbol": "QQQ", "name": "Invesco QQQ", "expense_ratio": "0.20"}
        result = format_fund_brief(data)
        assert "=== Fund Brief: QQQ ===" in result
        assert "expense_ratio: 0.20" in result

    def test_format_fund_allocation(self):
        data = {"allocations": [{"type": "Equity", "percent": "95.5"}]}
        result = format_fund_allocation(data)
        assert "=== Fund Allocation ===" in result
        assert "type: Equity" in result

    def test_format_fund_holdings(self):
        data = {"holdings": [{"target_symbol": "AAPL", "stock_name": "Apple",
                              "share_held_pct": "10.5", "share_held_chg_pct": "0.2",
                              "update_time": "2026-06-01"}]}
        result = format_fund_holdings(data)
        assert "=== Fund Holdings ===" in result
        assert "Symbol:          AAPL" in result
        assert "Weight (%):      10.5" in result

    def test_format_fund_performance(self):
        data = {"symbol": "QQQ", "ytd_return": "15.2%"}
        result = format_fund_performance(data)
        assert "=== Fund Performance: QQQ ===" in result
        assert "ytd_return: 15.2%" in result

    def test_format_fund_rating(self):
        data = {"rating_agency": "Morningstar", "rating_date": "2026-06-01",
                "rating_cycle": "3Y", "rating_results": "5"}
        result = format_fund_rating(data)
        assert "=== Fund Rating ===" in result
        assert "Rating Agency:   Morningstar" in result

    def test_format_fund_net_value(self):
        data = [{"date": "2026-06-20", "currency": "USD", "net_value": "450.5"}]
        result = format_fund_net_value(data)
        assert "=== Fund Net Value ===" in result
        assert "Net Value:       450.5" in result

    def test_format_fund_dividends(self):
        data = [{"share_date": "2026-03-15", "record_date": "2026-03-16",
                 "pay_date": "2026-03-30", "dps": "0.65"}]
        result = format_fund_dividends(data)
        assert "=== Fund Dividends ===" in result
        assert "DPS:             0.65" in result

    def test_format_fund_splits(self):
        data = [{"split_date": "2025-01-15", "ratio": "2:1"}]
        result = format_fund_splits(data)
        assert "=== Fund Splits ===" in result
        assert "ratio: 2:1" in result

    def test_format_fund_files(self):
        data = [{"file_name": "prospectus.pdf", "url": "https://example.com/p.pdf"}]
        result = format_fund_files(data)
        assert "=== Fund Files ===" in result
        assert "file_name: prospectus.pdf" in result


# ---------------------------------------------------------------------------
# Formatter tests: screener extended
# ---------------------------------------------------------------------------

class TestScreenerExtFormatters:
    def test_format_market_sectors(self):
        data = {"sectors": [{"sector_id": "10001", "sector_name": "Tech", "change_ratio": "0.03"}]}
        result = format_market_sectors(data)
        assert "=== Market Sectors ===" in result
        assert "sector_name: Tech" in result

    def test_format_market_sectors_detail(self):
        data = {"stocks": [{"symbol": "AAPL", "change_ratio": "0.02"}]}
        result = format_market_sectors_detail(data)
        assert "=== Market Sectors Detail ===" in result
        assert "symbol: AAPL" in result

    def test_format_high_dividend(self):
        data = [{"symbol": "T", "yield": "6.5"}]
        result = format_high_dividend(data)
        assert "=== High Dividend ===" in result
        assert "symbol: T" in result

    def test_format_52whl(self):
        data = [{"symbol": "TSLA", "change_ratio_52w": "0.85"}]
        result = format_52whl(data)
        assert "=== 52-Week High/Low ===" in result
        assert "symbol: TSLA" in result


# ---------------------------------------------------------------------------
# Integration tests: fundamentals module functions
# ---------------------------------------------------------------------------

class TestFundamentalsIntegration:
    def test_get_capital_flow(self):
        fund = _FakeFundamentals()
        sdk = _fake_sdk_fundamentals(fund)
        result = get_capital_flow(sdk, _config(), "AAPL", category="US_STOCK", count=3)
        assert "=== Capital Flow ===" in result
        assert "super_large_inflow: 100" in result
        assert fund.calls[0] == ("capital_flow", {"symbol": "AAPL", "category": "US_STOCK", "count": 3})

    def test_get_earnings_calendar(self):
        fund = _FakeFundamentals()
        sdk = _fake_sdk_fundamentals(fund)
        result = get_earnings_calendar(sdk, _config(), "AAPL", category="US_STOCK")
        assert "=== Earnings Calendar ===" in result
        assert "Fiscal Year:     2026" in result
        # eps_actual is None, should show as N/A via _get helper
        assert "EPS Actual:" in result

    def test_get_fund_brief(self):
        fund = _FakeFundamentals()
        sdk = _fake_sdk_fundamentals(fund)
        result = get_fund_brief(sdk, _config(), "QQQ", category="US_STOCK")
        assert "=== Fund Brief: QQQ ===" in result
        assert "expense_ratio: 0.20" in result

    def test_sdk_exception_handling(self):
        """Verify SDK exceptions are caught and formatted."""
        class _BrokenFundamentals:
            def get_capital_flow(self, **kwargs):
                raise RuntimeError("network timeout")

        sdk = _fake_sdk_fundamentals(_BrokenFundamentals())
        result = get_capital_flow(sdk, _config(), "AAPL")
        assert "Internal error" in result
        assert "network timeout" in result


# ---------------------------------------------------------------------------
# Integration tests: screener extended module functions
# ---------------------------------------------------------------------------

class TestScreenerExtIntegration:
    def test_get_market_sectors(self):
        screener = _FakeScreenerExt()
        sdk = _fake_sdk_screener(screener)
        result = get_market_sectors(sdk, _config(), category="US_STOCK", period="D1")
        assert "=== Market Sectors ===" in result
        assert "sector_name: Technology" in result
        assert screener.calls[0][1]["category"] == "US_STOCK"
        assert screener.calls[0][1]["period"] == "D1"

    def test_get_high_dividend(self):
        screener = _FakeScreenerExt()
        sdk = _fake_sdk_screener(screener)
        result = get_high_dividend(sdk, _config(), category="US_STOCK", sort_by="YIELD")
        assert "=== High Dividend ===" in result
        assert "symbol: T" in result
        assert screener.calls[0][1]["sort_by"] == "YIELD"
