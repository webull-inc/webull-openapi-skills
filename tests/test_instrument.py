"""Unit tests for instrument fundamentals (company profile, analyst rating/target price)."""

from __future__ import annotations

from types import SimpleNamespace

from webull_skill.trading.instrument import (
    get_company_profile,
    get_analyst_rating,
    get_analyst_target_price,
    get_futures_product_class,
    get_futures_products,
    get_futures_instruments,
    get_futures_instruments_by_code,
)


class _FakeResponse:
    def __init__(self, data: object) -> None:
        self._data = data

    def json(self) -> object:
        return self._data


class _FakeInstrument:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def get_company_profile(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_company_profile", kwargs))
        return _FakeResponse({
            "symbol": "NVDA",
            "category": "US_STOCK",
            "company_name": "NVIDIA Corp",
            "establish_date": "1998-02-24",
            "exhibition_code": "NASDAQ",
            "profile": "NVIDIA Corporation is a full-stack computing infrastructure company.",
            "employees": "36000",
            "address": "2788 San Tomas Expressway,SANTA CLARA,CA,United States",
            "ceo": "Jen-Hsun Huang",
            "industries": ["Semiconductors", "Semiconductors & Semiconductor Equipment"],
        })

    def get_analyst_rating(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_analyst_rating", kwargs))
        return _FakeResponse({
            "symbol": "NVDA",
            "category": "US_STOCK",
            "number": "58",
            "under_perform": "0",
            "buy": "11",
            "sell": "0",
            "strong_buy": "43",
            "hold": "4",
            "effective_start_date": "2021-12-29T06:24:56.038+0000",
        })

    def get_analyst_target_price(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_analyst_target_price", kwargs))
        return _FakeResponse({
            "symbol": "NVDA",
            "category": "US_STOCK",
            "mean": "85.0",
            "low": "85.0",
            "high": "200.0",
            "median": "139.72",
            "currency": "USD",
            "effective_start_date": "2021-12-29T06:24:56.038+0000",
        })

    def get_futures_product_class(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_futures_product_class", kwargs))
        return _FakeResponse([
            {
                "product_class_id": 1,
                "product_class_name": "Energy",
            },
            {
                "product_class_id": 2,
                "product_class_name": "Equities",
            },
        ])

    def get_futures_products(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_futures_products", kwargs))
        return _FakeResponse([
            {
                "product_code": "ES",
                "name": "E-mini S&P 500",
                "exchange": "CME",
            },
            {
                "product_code": "NQ",
                "name": "E-mini Nasdaq 100",
                "exchange": "CME",
            },
        ])

    def get_futures_instrument(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_futures_instrument", kwargs))
        return _FakeResponse([
            {
                "symbol": "ESM6",
                "name": "E-mini S&P 500 Jun 2026",
                "instrument_type": "FUTURES",
                "exchange": "CME",
            },
        ])

    def get_futures_instrument_by_code(self, **kwargs: object) -> _FakeResponse:
        self.calls.append(("get_futures_instrument_by_code", kwargs))
        return _FakeResponse([
            {
                "symbol": "ESM6",
                "name": "E-mini S&P 500 Jun 2026",
                "instrument_type": "FUTURES",
                "exchange": "CME",
            },
            {
                "symbol": "ESU6",
                "name": "E-mini S&P 500 Sep 2026",
                "instrument_type": "FUTURES",
                "exchange": "CME",
            },
        ])


def _fake_sdk(instrument: _FakeInstrument) -> object:
    data = SimpleNamespace(instrument=instrument)
    return SimpleNamespace(data=data, region_id="us")


def test_get_company_profile_formats_all_fields():
    inst = _FakeInstrument()
    result = get_company_profile(_fake_sdk(inst), symbol="NVDA", category="US_STOCK")

    assert "=== Company Profile: NVDA ===" in result
    assert "NVIDIA Corp" in result
    assert "1998-02-24" in result
    assert "Jen-Hsun Huang" in result
    assert "36000" in result
    assert "NASDAQ" in result
    assert "Semiconductors" in result
    assert "full-stack computing" in result
    assert inst.calls[0] == ("get_company_profile", {"symbol": "NVDA", "category": "US_STOCK"})


def test_get_analyst_rating_formats_all_fields():
    inst = _FakeInstrument()
    result = get_analyst_rating(_fake_sdk(inst), symbol="NVDA", category="US_STOCK")

    assert "=== Analyst Rating: NVDA ===" in result
    assert "Total Analysts:  58" in result
    assert "Strong Buy:      43" in result
    assert "Buy:             11" in result
    assert "Hold:            4" in result
    assert "Underperform:    0" in result
    assert "Sell:            0" in result
    assert "Effective Date:" in result
    assert inst.calls[0] == ("get_analyst_rating", {"symbol": "NVDA", "category": "US_STOCK"})


def test_get_analyst_target_price_formats_all_fields():
    inst = _FakeInstrument()
    result = get_analyst_target_price(_fake_sdk(inst), symbol="NVDA", category="US_STOCK")

    assert "=== Analyst Target Price: NVDA ===" in result
    assert "Mean Target:     85.0" in result
    assert "Median Target:   139.72" in result
    assert "High Target:     200.0" in result
    assert "Low Target:      85.0" in result
    assert "Currency:        USD" in result
    assert "Effective Date:" in result
    assert inst.calls[0] == ("get_analyst_target_price", {"symbol": "NVDA", "category": "US_STOCK"})


# ---------------------------------------------------------------------------
# Futures product classes tests
# ---------------------------------------------------------------------------


def test_get_futures_product_class_formats_response():
    inst = _FakeInstrument()
    result = get_futures_product_class(_fake_sdk(inst), category="US_FUTURES")

    assert "=== Futures Product Classes ===" in result
    assert "Energy" in result
    assert "Equities" in result
    assert "Class ID:        1" in result
    assert "Class ID:        2" in result
    assert "Class Name:      Energy" in result
    assert "Class Name:      Equities" in result
    assert inst.calls[0] == ("get_futures_product_class", {"category": "US_FUTURES"})


def test_get_futures_product_class_hk_futures_category():
    inst = _FakeInstrument()
    result = get_futures_product_class(_fake_sdk(inst), category="HK_FUTURES")

    assert "=== Futures Product Classes ===" in result
    assert inst.calls[0] == ("get_futures_product_class", {"category": "HK_FUTURES"})


# ---------------------------------------------------------------------------
# Futures products tests
# ---------------------------------------------------------------------------


def test_get_futures_products_formats_response():
    inst = _FakeInstrument()
    result = get_futures_products(_fake_sdk(inst), category="US_FUTURES")

    assert "=== Futures Products ===" in result
    assert "ES" in result
    assert "NQ" in result
    assert "E-mini S&P 500" in result
    assert "E-mini Nasdaq 100" in result
    assert "CME" in result
    assert inst.calls[0] == ("get_futures_products", {"category": "US_FUTURES"})


def test_get_futures_products_hk_futures_category():
    inst = _FakeInstrument()
    result = get_futures_products(_fake_sdk(inst), category="HK_FUTURES")

    assert "=== Futures Products ===" in result
    assert inst.calls[0] == ("get_futures_products", {"category": "HK_FUTURES"})


# ---------------------------------------------------------------------------
# Futures instruments tests
# ---------------------------------------------------------------------------


def test_get_futures_instruments_formats_response():
    inst = _FakeInstrument()
    result = get_futures_instruments(_fake_sdk(inst), symbols="ESM6", category="US_FUTURES")

    assert "=== Instruments ===" in result
    assert "ESM6" in result
    assert "E-mini S&P 500 Jun 2026" in result
    assert "FUTURES" in result
    assert "CME" in result
    assert inst.calls[0] == ("get_futures_instrument", {"symbols": ["ESM6"], "category": "US_FUTURES"})


def test_get_futures_instruments_multiple_symbols():
    inst = _FakeInstrument()
    result = get_futures_instruments(_fake_sdk(inst), symbols="ESM6,NQM6", category="US_FUTURES")

    assert "=== Instruments ===" in result
    assert inst.calls[0] == ("get_futures_instrument", {"symbols": ["ESM6", "NQM6"], "category": "US_FUTURES"})


# ---------------------------------------------------------------------------
# Futures instruments by code tests
# ---------------------------------------------------------------------------


def test_get_futures_instruments_by_code_formats_response():
    inst = _FakeInstrument()
    result = get_futures_instruments_by_code(_fake_sdk(inst), code="ES", category="US_FUTURES")

    assert "=== Instruments ===" in result
    assert "ESM6" in result
    assert "ESU6" in result
    assert "E-mini S&P 500 Jun 2026" in result
    assert "E-mini S&P 500 Sep 2026" in result
    assert inst.calls[0] == ("get_futures_instrument_by_code", {"code": "ES", "category": "US_FUTURES"})


def test_get_futures_instruments_by_code_with_contract_type():
    inst = _FakeInstrument()
    result = get_futures_instruments_by_code(
        _fake_sdk(inst), code="ES", category="US_FUTURES", contract_type="MONTHLY"
    )

    assert "=== Instruments ===" in result
    assert inst.calls[0] == (
        "get_futures_instrument_by_code",
        {"code": "ES", "category": "US_FUTURES", "contract_type": "MONTHLY"},
    )
