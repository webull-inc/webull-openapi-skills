#!/usr/bin/env python3
"""Unified CLI entry point for Webull OpenAPI Skill.

Usage:
    webull-skill trading --action stock-snapshot --symbols AAPL
    webull-skill market-data --action stock-snapshot --symbols AAPL
    webull-skill auth --env-file .env
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from webull_skill.audit import AuditLogger
from webull_skill.config import SkillConfig, load_config, validate_config
from webull_skill.errors import ConfigError
from webull_skill.formatters import set_disclaimer_region
from webull_skill.result import OperationResult, success, failure, default_category
from webull_skill.runtime import set_sdk_logging


# ---------------------------------------------------------------------------
# Action lists
# ---------------------------------------------------------------------------

TRADING_ACTIONS = [
    # Instrument queries
    "instrument-stock", "instrument-crypto",
    "instrument-futures-products", "instrument-futures-product-class",
    "instrument-futures-list",
    "instrument-futures-by-code",
    "instrument-event-series", "instrument-event-list",
    "instrument-event-categories", "instrument-event-events",
    # Instrument fundamentals
    "instrument-company-profile", "instrument-analyst-rating",
    "instrument-analyst-target-price",
    # Account / asset
    "account-list", "balance", "position", "position-detail",
    # Order operations
    "place", "preview", "replace", "batch-place",
    "cancel", "open", "history", "detail",
    "option-place", "option-preview", "option-replace",
    "option-strategy-place",
    "futures-place", "futures-replace",
    "crypto-place", "event-place", "event-replace",
    "algo-place", "local-check",
]

MARKET_DATA_ACTIONS = [
    # Stock
    "stock-snapshot", "stock-bars", "stock-batch-bars",
    "stock-tick", "stock-quotes", "stock-footprint",
    "stock-noii-bars", "stock-noii-snapshot",
    # Futures
    "futures-snapshot", "futures-bars", "futures-tick",
    "futures-depth", "futures-footprint",
    # Crypto
    "crypto-snapshot", "crypto-bars",
    # Event
    "event-snapshot", "event-depth", "event-bars", "event-tick",
    # Screener
    "stock-gainers-losers", "stock-most-active",
    # Watchlist
    "watchlist-list", "watchlist-create", "watchlist-delete", "watchlist-update",
    "watchlist-instruments-list", "watchlist-instruments-add",
    "watchlist-instruments-remove", "watchlist-instruments-update",
]


_JP_UNSUPPORTED_TRADING_ACTIONS = frozenset({
    "instrument-crypto",
    "instrument-futures-products",
    "instrument-futures-product-class",
    "instrument-futures-list",
    "instrument-futures-by-code",
    "instrument-event-series",
    "instrument-event-list",
    "instrument-event-categories",
    "instrument-event-events",
    "batch-place",
    "algo-place",
    "option-place",
    "option-preview",
    "option-replace",
    "option-strategy-place",
    "futures-place",
    "futures-replace",
    "crypto-place",
    "event-place",
    "event-replace",
})

_JP_STOCK_INSTRUMENT_CATEGORIES = frozenset({"US_STOCK", "US_ETF"})


def _region_trading_error(config: SkillConfig, action: str, category: str) -> str:
    """Return a validation error for unsupported region/action pairs."""
    region_id = config.region_id.lower()
    if action == "position-detail" and region_id != "jp":
        return "Action 'position-detail' is only supported in region 'jp'"
    if region_id != "jp":
        # 期货 instrument 查询的 category 验证（仅 US 和 HK 支持）
        futures_actions = {
            "instrument-futures-products",
            "instrument-futures-product-class",
            "instrument-futures-list",
            "instrument-futures-by-code",
        }
        if action in futures_actions:
            from webull_skill.constants import (
                VALID_FUTURES_CATEGORIES_HK,
                VALID_FUTURES_CATEGORIES_US,
            )
            if region_id == "us":
                valid_cats = VALID_FUTURES_CATEGORIES_US
            elif region_id == "hk":
                valid_cats = VALID_FUTURES_CATEGORIES_HK
            else:
                return f"Action '{action}' is not supported in region '{region_id}'"
            if category and category not in valid_cats:
                valid = ", ".join(sorted(valid_cats))
                return f"Invalid futures category '{category}' for region '{region_id}'. Valid values: {valid}"
        return ""
    if action in _JP_UNSUPPORTED_TRADING_ACTIONS:
        return f"Action '{action}' is not supported in region 'jp'"
    if action == "instrument-stock" and category not in _JP_STOCK_INSTRUMENT_CATEGORIES:
        valid = ", ".join(sorted(_JP_STOCK_INSTRUMENT_CATEGORIES))
        return f"Invalid instrument category '{category}' for region 'jp'. Valid values: {valid}"
    return ""


def _region_market_data_error(config: SkillConfig, action: str) -> str:
    """Return a validation error for unsupported market-data actions."""
    region_id = config.region_id.lower()

    # Screener 和 Watchlist 全市场支持，无需区域限制

    if region_id != "jp":
        return ""
    if not action.startswith("stock-") and not action.startswith("watchlist-"):
        return f"Market data action '{action}' is not supported in region 'jp'"
    return ""


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Webull OpenAPI Skill CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Common arguments
    parser.add_argument(
        "--env-file",
        default=None,
        help="Path to .env file (default: .env in current directory)",
    )
    parser.add_argument("--verbose-sdk-log", action="store_true", help="Enable verbose SDK logging")

    subparsers = parser.add_subparsers(dest="module", help="Command module")

    # trading subcommand
    tp = subparsers.add_parser("trading", help="Instrument queries, account/asset, and order operations")
    tp.add_argument("--action", required=True, choices=TRADING_ACTIONS)
    tp.add_argument("--symbol", default="")
    tp.add_argument("--symbols", default="")
    tp.add_argument("--category", default="")
    tp.add_argument("--account-id", default="")
    tp.add_argument("--instrument-id", default="")
    tp.add_argument("--last-id", default="")
    tp.add_argument("--code", default="")
    tp.add_argument("--series-symbol", default="")
    tp.add_argument("--page-size", type=int, default=500)
    tp.add_argument("--order-json", default="")
    tp.add_argument("--order-file", default="")
    tp.add_argument("--client-order-id", default="")

    # market-data subcommand
    mp = subparsers.add_parser("market-data", help="Market data queries")
    mp.add_argument("--action", required=True, choices=MARKET_DATA_ACTIONS)
    mp.add_argument("--symbol", default="")
    mp.add_argument("--symbols", default="")
    mp.add_argument("--category", default="")
    mp.add_argument("--timespan", default="D")
    mp.add_argument("--count", type=int, default=200)
    mp.add_argument("--depth", type=int, default=1)
    mp.add_argument("--trading-sessions", default="")
    mp.add_argument("--real-time-required", action="store_true")
    mp.add_argument("--extend-hour-required", action="store_true")
    mp.add_argument("--overnight-required", action="store_true")
    # K线时间范围（long 毫秒时间戳）
    mp.add_argument("--start-time", type=int, default=None, help="Start timestamp in milliseconds (Long)")
    mp.add_argument("--end-time", type=int, default=None, help="End timestamp in milliseconds (Long)")
    # NOII
    mp.add_argument("--imbalance-action-type", default="PRE_OPEN",
                    choices=["PRE_OPEN", "PRE_CLOSE"],
                    help="NOII imbalance action type: PRE_OPEN or PRE_CLOSE")
    # Screener
    mp.add_argument("--rank-type", default="", help="Rank type for screener (e.g. DAY_1, VOLUME)")
    mp.add_argument("--sort-by", default="", help="Secondary sort field for screener")
    mp.add_argument("--direction", default="", help="Sort direction: ASC or DESC")
    mp.add_argument("--page-index", type=int, default=None, help="Page number starting from 1")
    mp.add_argument("--page-size", type=int, default=None, help="Records per page")
    # Watchlist
    mp.add_argument("--watchlist-id", default="", help="Watchlist unique identifier")
    mp.add_argument("--watchlist-name", default="", help="Watchlist name")
    mp.add_argument("--watchlist-sort", type=int, default=None, help="Watchlist sort order")
    mp.add_argument("--instruments-json", default="",
                    help="JSON array of instruments for watchlist operations, "
                         "e.g. '[{\"symbol\":\"AAPL\",\"category\":\"US_STOCK\"}]'")

    # auth subcommand
    subparsers.add_parser("auth", help="Authenticate and obtain access token (interactive 2FA)")

    return parser


def load_orders(args: argparse.Namespace) -> list[dict]:
    """Load orders from --order-json or --order-file."""
    raw = ""
    if args.order_json:
        raw = args.order_json
    elif args.order_file:
        p = Path(args.order_file)
        if not p.exists():
            raise ValueError(f"Order file not found: {args.order_file}")
        raw = p.read_text(encoding="utf-8")
    if not raw:
        return []
    data = json.loads(raw)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("Order JSON must be a dict or list of dicts")


def _wrap_tool_result(tool_result: str, action: str) -> str | OperationResult:
    """Return tool result directly on success, or OperationResult on error."""
    error_prefixes = ("Account error:", "Validation error:", "Server error", "Parameter error:", "Internal error:")
    if any(tool_result.startswith(p) for p in error_prefixes):
        return failure(detail=tool_result)
    return tool_result


def dispatch_trading(args: argparse.Namespace, config: SkillConfig) -> str | OperationResult:
    """Dispatch a trading subcommand action. Returns formatted string or OperationResult on error."""
    action = args.action
    cat = args.category or default_category(action)
    symbols_str = args.symbols or args.symbol
    aid = args.account_id

    region_error = _region_trading_error(config, action, cat)
    if region_error:
        return failure(detail=f"Validation error: {region_error}")

    from webull_skill.risk_engine import RiskEngine
    from webull_skill.sdk_client import SDKClient
    from webull_skill.trading.account import get_account_list
    from webull_skill.trading.assets import (
        get_account_balance,
        get_account_position_details,
        get_account_positions,
    )
    from webull_skill.trading.instrument import (
        get_instruments,
        get_crypto_instruments,
        get_futures_products,
        get_futures_product_class,
        get_futures_instruments,
        get_futures_instruments_by_code,
        get_event_series,
        get_event_instruments,
        get_event_categories,
        get_event_events,
        get_company_profile,
        get_analyst_rating,
        get_analyst_target_price,
    )
    from webull_skill.trading.order import (
        cancel_order,
        get_order_history,
        get_open_orders,
        get_order_detail,
    )
    from webull_skill.trading.stock_order import (
        place_stock_order,
        preview_stock_order,
        replace_stock_order,
        place_stock_combo_order,
        place_algo_order,
    )
    from webull_skill.trading.option_order import (
        place_option_single_order,
        preview_option_order,
        replace_option_order,
        place_option_strategy_order,
    )
    from webull_skill.trading.futures_order import place_futures_order, replace_futures_order
    from webull_skill.trading.crypto_order import place_crypto_order
    from webull_skill.trading.event_order import place_event_order, replace_event_order

    sdk = SDKClient(config)
    sdk.initialize()

    # -- Instrument queries -------------------------------------------------
    if action == "instrument-stock":
        return _wrap_tool_result(get_instruments(sdk, symbols_str, category=cat), action)
    if action == "instrument-crypto":
        return _wrap_tool_result(get_crypto_instruments(sdk, symbols_str, category=cat), action)
    if action == "instrument-futures-products":
        return _wrap_tool_result(get_futures_products(sdk, category=cat), action)
    if action == "instrument-futures-product-class":
        return _wrap_tool_result(get_futures_product_class(sdk, category=cat), action)
    if action == "instrument-futures-list":
        return _wrap_tool_result(get_futures_instruments(sdk, symbols_str, category=cat), action)
    if action == "instrument-futures-by-code":
        return _wrap_tool_result(get_futures_instruments_by_code(sdk, code=args.code, category=cat), action)
    if action == "instrument-event-series":
        return _wrap_tool_result(get_event_series(sdk, category=cat, page_size=args.page_size), action)
    if action == "instrument-event-list":
        return _wrap_tool_result(get_event_instruments(sdk, series_symbol=args.series_symbol, page_size=args.page_size), action)
    if action == "instrument-event-categories":
        return _wrap_tool_result(get_event_categories(sdk), action)
    if action == "instrument-event-events":
        return _wrap_tool_result(get_event_events(sdk, series_symbol=args.series_symbol), action)

    # -- Instrument fundamentals --------------------------------------------
    if action == "instrument-company-profile":
        sym = symbols_str or args.symbol
        if not sym:
            return failure(detail="--symbol is required for instrument-company-profile")
        return _wrap_tool_result(get_company_profile(sdk, symbol=sym, category=cat or "US_STOCK"), action)
    if action == "instrument-analyst-rating":
        sym = symbols_str or args.symbol
        if not sym:
            return failure(detail="--symbol is required for instrument-analyst-rating")
        return _wrap_tool_result(get_analyst_rating(sdk, symbol=sym, category=cat or "US_STOCK"), action)
    if action == "instrument-analyst-target-price":
        sym = symbols_str or args.symbol
        if not sym:
            return failure(detail="--symbol is required for instrument-analyst-target-price")
        return _wrap_tool_result(get_analyst_target_price(sdk, symbol=sym, category=cat or "US_STOCK"), action)

    # -- Account / asset ----------------------------------------------------
    if action == "account-list":
        return _wrap_tool_result(get_account_list(sdk), action)
    if action == "balance":
        if not aid:
            return failure(detail="--account-id is required for balance")
        return _wrap_tool_result(get_account_balance(sdk, aid), action)
    if action == "position":
        if not aid:
            return failure(detail="--account-id is required for position")
        return _wrap_tool_result(get_account_positions(sdk, aid), action)
    if action == "position-detail":
        if not aid:
            return failure(detail="--account-id is required for position-detail")
        if not args.instrument_id:
            return failure(detail="--instrument-id is required for position-detail")
        page_size = args.page_size if args.page_size != 500 else 20
        return _wrap_tool_result(
            get_account_position_details(
                sdk,
                config,
                account_id=aid,
                instrument_id=args.instrument_id,
                page_size=page_size,
                last_id=args.last_id or None,
            ),
            action,
        )

    # -- Load orders for order actions --------------------------------------
    orders: list[dict] = []
    order_actions = {
        "place", "preview", "replace", "batch-place",
        "option-place", "option-preview", "option-replace",
        "option-strategy-place",
        "futures-place", "futures-replace",
        "crypto-place", "event-place", "event-replace",
        "algo-place", "local-check",
    }
    if action in order_actions:
        try:
            orders = load_orders(args)
        except (ValueError, json.JSONDecodeError) as exc:
            return failure(detail=f"Failed to load orders: {exc}")

    # -- Stock orders -------------------------------------------------------
    if action == "place":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        # Map JSON field names to function param names, drop fields handled internally
        mapped: dict[str, Any] = {
            "symbol": o.get("symbol"),
            "side": o.get("side"),
            "order_type": o.get("order_type"),
            "time_in_force": o.get("time_in_force"),
            "quantity": float(o["quantity"]) if "quantity" in o else None,
            "market": o.get("market", "US"),
            "limit_price": float(o["limit_price"]) if o.get("limit_price") else None,
            "stop_price": float(o["stop_price"]) if o.get("stop_price") else None,
            "entrust_type": o.get("entrust_type", "QTY"),
            "total_cash_amount": float(o["total_cash_amount"]) if o.get("total_cash_amount") else None,
            "trading_session": o.get("support_trading_session", o.get("trading_session", "CORE")),
            "extended_hours": o.get("extended_hours", False),
            "trailing_type": o.get("trailing_type"),
            "trailing_stop_step": float(o["trailing_stop_step"]) if o.get("trailing_stop_step") else None,
            "client_order_id": o.get("client_order_id"),
            "sender_sub_id": o.get("sender_sub_id"),
            "no_party_ids": o.get("no_party_ids"),
            "account_tax_type": o.get("account_tax_type"),
            "margin_type": o.get("margin_type"),
            "position_intent": o.get("position_intent"),
            "close_contracts": o.get("close_contracts"),
        }
        # Remove None values so defaults in function signature apply
        mapped = {k: v for k, v in mapped.items() if v is not None}
        return _wrap_tool_result(
            place_stock_order(sdk, config, account_id=aid, **mapped), action
        )
    if action == "preview":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            preview_stock_order(sdk, aid, config=config, **o), action
        )
    if action == "replace":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        if len(orders) > 1:
            return _wrap_tool_result(
                replace_stock_order(sdk, aid, orders=orders, config=config), action
            )
        o = orders[0]
        return _wrap_tool_result(
            replace_stock_order(sdk, aid, config=config, **o), action
        )
    if action == "batch-place":
        if not aid:
            return failure(detail="--account-id required")
        return _wrap_tool_result(
            place_stock_combo_order(sdk, aid, orders), action
        )

    # -- Option orders ------------------------------------------------------
    if action == "option-place":
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            place_option_single_order(sdk, config, account_id=aid or None, **o), action
        )
    if action == "option-preview":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            preview_option_order(sdk, config, aid, **o), action
        )
    if action == "option-replace":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            replace_option_order(sdk, aid, **o), action
        )
    if action == "option-strategy-place":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            place_option_strategy_order(sdk, config, aid, **o), action
        )

    # -- Futures orders -----------------------------------------------------
    if action == "futures-place":
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            place_futures_order(sdk, config, account_id=aid or None, **o), action
        )
    if action == "futures-replace":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            replace_futures_order(sdk, aid, **o), action
        )

    # -- Crypto orders ------------------------------------------------------
    if action == "crypto-place":
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            place_crypto_order(sdk, config, account_id=aid or None, **o), action
        )

    # -- Event orders -------------------------------------------------------
    if action == "event-place":
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            place_event_order(sdk, config, account_id=aid or None, **o), action
        )
    if action == "event-replace":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            replace_event_order(sdk, aid, **o), action
        )

    # -- Algo orders --------------------------------------------------------
    if action == "algo-place":
        if not aid:
            return failure(detail="--account-id required")
        if not orders:
            return failure(detail="No order data provided")
        o = orders[0]
        return _wrap_tool_result(
            place_algo_order(sdk, aid, **o), action
        )

    # -- Order management ---------------------------------------------------
    if action == "cancel":
        if not aid:
            return failure(detail="--account-id required")
        if not args.client_order_id:
            return failure(detail="--client-order-id required")
        return _wrap_tool_result(cancel_order(sdk, aid, args.client_order_id), action)
    if action == "open":
        if not aid:
            return failure(detail="--account-id required")
        return _wrap_tool_result(get_open_orders(sdk, aid), action)
    if action == "history":
        if not aid:
            return failure(detail="--account-id required")
        return _wrap_tool_result(get_order_history(sdk, aid), action)
    if action == "detail":
        if not aid:
            return failure(detail="--account-id required")
        if not args.client_order_id:
            return failure(detail="--client-order-id required")
        return _wrap_tool_result(get_order_detail(sdk, aid, args.client_order_id), action)

    # -- Local risk check ---------------------------------------------------
    if action == "local-check":
        risk = RiskEngine(config)
        result = risk.check_orders(orders)
        if result.allowed:
            return "Risk check passed: order is within configured limits."
        lines = ["Risk check FAILED:"]
        for v in result.violations:
            prefix = f"  Order[{v.order_index}]" if v.order_index is not None else "  "
            lines.append(f"{prefix} {v.field}: {v.message}")
        return "\n".join(lines)

    return failure(detail=f"Unknown trading action: {action}")


def dispatch_market_data(args: argparse.Namespace, config: SkillConfig) -> str | OperationResult:
    """Dispatch a market-data subcommand action. Returns formatted string or OperationResult on error."""
    action = args.action
    region_error = _region_market_data_error(config, action)
    if region_error:
        return failure(detail=f"Validation error: {region_error}")

    from webull_skill.market_data.crypto import get_crypto_snapshot, get_crypto_bars
    from webull_skill.market_data.event import (
        get_event_snapshot,
        get_event_depth,
        get_event_bars,
        get_event_tick,
    )
    from webull_skill.market_data.futures import (
        get_futures_snapshot,
        get_futures_bars,
        get_futures_tick,
        get_futures_depth,
        get_futures_footprint,
    )
    from webull_skill.market_data.screener import get_gainers_losers, get_most_active
    from webull_skill.market_data.stock import (
        get_stock_snapshot,
        get_stock_bars,
        get_stock_bars_single,
        get_stock_tick,
        get_stock_quotes,
        get_stock_footprint,
        get_stock_noii_bars,
        get_stock_noii_snapshot,
    )
    from webull_skill.market_data.watchlist import (
        get_watchlist,
        create_watchlist,
        delete_watchlist,
        update_watchlist,
        get_watchlist_instruments,
        add_watchlist_instruments,
        remove_watchlist_instruments,
        update_watchlist_instruments,
    )
    from webull_skill.sdk_client import SDKClient

    sdk = SDKClient(config)
    sdk.initialize()

    cat = args.category or default_category(action)
    symbols_str = args.symbols or args.symbol
    symbol = args.symbol or (symbols_str.split(",")[0].strip() if symbols_str else "")

    # Stock
    if action == "stock-snapshot":
        return _wrap_tool_result(
            get_stock_snapshot(sdk, config, symbols_str, category=cat,
                              extend_hour_required=args.extend_hour_required,
                              overnight_required=args.overnight_required),
            action,
        )
    if action == "stock-bars":
        return _wrap_tool_result(
            get_stock_bars_single(sdk, config, symbol, category=cat,
                                 timespan=args.timespan, count=args.count,
                                 trading_sessions=args.trading_sessions or None,
                                 start_time=args.start_time,
                                 end_time=args.end_time),
            action,
        )
    if action == "stock-batch-bars":
        return _wrap_tool_result(
            get_stock_bars(sdk, config, symbols_str, category=cat,
                           timespan=args.timespan, count=args.count,
                           trading_sessions=args.trading_sessions or None,
                           start_time=args.start_time,
                           end_time=args.end_time),
            action,
        )
    if action == "stock-tick":
        return _wrap_tool_result(
            get_stock_tick(sdk, config, symbol, category=cat, count=args.count,
                           trading_sessions=args.trading_sessions or None),
            action,
        )
    if action == "stock-quotes":
        return _wrap_tool_result(
            get_stock_quotes(sdk, config, symbol, category=cat,
                             overnight_required=args.overnight_required),
            action,
        )
    if action == "stock-footprint":
        return _wrap_tool_result(
            get_stock_footprint(sdk, config, symbols_str, category=cat,
                                timespan=args.timespan, count=args.count,
                                real_time_required=args.real_time_required,
                                trading_sessions=args.trading_sessions or None),
            action,
        )

    # Futures
    if action == "futures-snapshot":
        return _wrap_tool_result(
            get_futures_snapshot(sdk, config, symbols_str, category=cat), action,
        )
    if action == "futures-bars":
        return _wrap_tool_result(
            get_futures_bars(sdk, config, symbols_str, category=cat,
                             timespan=args.timespan, count=args.count,
                             real_time_required=args.real_time_required),
            action,
        )
    if action == "futures-tick":
        return _wrap_tool_result(
            get_futures_tick(sdk, config, symbol, category=cat, count=args.count), action,
        )
    if action == "futures-depth":
        return _wrap_tool_result(
            get_futures_depth(sdk, config, symbol, category=cat, depth=args.depth), action,
        )
    if action == "futures-footprint":
        return _wrap_tool_result(
            get_futures_footprint(sdk, config, symbols_str, category=cat,
                                  timespan=args.timespan, count=args.count,
                                  real_time_required=args.real_time_required,
                                  trading_sessions=args.trading_sessions or None),
            action,
        )

    # Crypto
    if action == "crypto-snapshot":
        return _wrap_tool_result(
            get_crypto_snapshot(sdk, config, symbols_str, category=cat), action,
        )
    if action == "crypto-bars":
        return _wrap_tool_result(
            get_crypto_bars(sdk, config, symbols_str, category=cat,
                            timespan=args.timespan, count=args.count,
                            real_time_required=args.real_time_required),
            action,
        )

    # Event
    if action == "event-snapshot":
        return _wrap_tool_result(
            get_event_snapshot(sdk, config, symbols_str, category=cat), action,
        )
    if action == "event-depth":
        return _wrap_tool_result(
            get_event_depth(sdk, config, symbol, category=cat, depth=args.depth), action,
        )
    if action == "event-bars":
        return _wrap_tool_result(
            get_event_bars(sdk, config, symbols_str, category=cat,
                           timespan=args.timespan, count=args.count,
                           real_time_required=args.real_time_required),
            action,
        )
    if action == "event-tick":
        return _wrap_tool_result(
            get_event_tick(sdk, config, symbol, category=cat, count=args.count), action,
        )

    # NOII
    if action == "stock-noii-bars":
        if not symbol:
            return failure(detail="--symbol is required for stock-noii-bars")
        return _wrap_tool_result(
            get_stock_noii_bars(sdk, config, symbol=symbol, category=cat or "US_STOCK",
                                imbalance_action_type=args.imbalance_action_type),
            action,
        )
    if action == "stock-noii-snapshot":
        if not symbol:
            return failure(detail="--symbol is required for stock-noii-snapshot")
        return _wrap_tool_result(
            get_stock_noii_snapshot(sdk, config, symbol=symbol, category=cat or "US_STOCK",
                                    imbalance_action_type=args.imbalance_action_type),
            action,
        )

    # Screener
    if action == "stock-gainers-losers":
        if not args.rank_type:
            return failure(detail="--rank-type is required for stock-gainers-losers")
        return _wrap_tool_result(
            get_gainers_losers(
                sdk, config,
                rank_type=args.rank_type,
                category=cat or "US_STOCK",
                sort_by=args.sort_by or "CHANGE_RATIO",
                direction=args.direction or None,
                page_index=args.page_index,
                page_size=args.page_size,
            ),
            action,
        )
    if action == "stock-most-active":
        return _wrap_tool_result(
            get_most_active(
                sdk, config,
                category=cat or "US_STOCK",
                rank_type=args.rank_type or None,
                sort_by=args.sort_by or None,
                direction=args.direction or None,
                page_index=args.page_index,
                page_size=args.page_size,
            ),
            action,
        )

    # Watchlist
    if action == "watchlist-list":
        return _wrap_tool_result(get_watchlist(sdk, config), action)

    if action == "watchlist-create":
        if not args.watchlist_name:
            return failure(detail="--watchlist-name is required for watchlist-create")
        return _wrap_tool_result(
            create_watchlist(sdk, config, name=args.watchlist_name, sort=args.watchlist_sort),
            action,
        )
    if action == "watchlist-delete":
        if not args.watchlist_id:
            return failure(detail="--watchlist-id is required for watchlist-delete")
        return _wrap_tool_result(delete_watchlist(sdk, config, watchlist_id=args.watchlist_id), action)

    if action == "watchlist-update":
        if not args.watchlist_id:
            return failure(detail="--watchlist-id is required for watchlist-update")
        return _wrap_tool_result(
            update_watchlist(
                sdk, config,
                watchlist_id=args.watchlist_id,
                name=args.watchlist_name or None,
                sort=args.watchlist_sort,
            ),
            action,
        )
    if action == "watchlist-instruments-list":
        if not args.watchlist_id:
            return failure(detail="--watchlist-id is required for watchlist-instruments-list")
        return _wrap_tool_result(
            get_watchlist_instruments(sdk, config, watchlist_id=args.watchlist_id), action
        )

    # Watchlist instrument mutation actions — parse --instruments-json
    _watchlist_instrument_actions = {
        "watchlist-instruments-add",
        "watchlist-instruments-remove",
        "watchlist-instruments-update",
    }
    if action in _watchlist_instrument_actions:
        if not args.watchlist_id:
            return failure(detail=f"--watchlist-id is required for {action}")
        if not args.instruments_json:
            return failure(detail=f"--instruments-json is required for {action}")
        try:
            instruments = json.loads(args.instruments_json)
            if not isinstance(instruments, list):
                return failure(detail="--instruments-json must be a JSON array")
        except json.JSONDecodeError as exc:
            return failure(detail=f"Invalid --instruments-json: {exc}")

        if action == "watchlist-instruments-add":
            return _wrap_tool_result(
                add_watchlist_instruments(sdk, config, watchlist_id=args.watchlist_id,
                                          instruments=instruments),
                action,
            )
        if action == "watchlist-instruments-remove":
            return _wrap_tool_result(
                remove_watchlist_instruments(sdk, config, watchlist_id=args.watchlist_id,
                                             instruments=instruments),
                action,
            )
        if action == "watchlist-instruments-update":
            return _wrap_tool_result(
                update_watchlist_instruments(sdk, config, watchlist_id=args.watchlist_id,
                                             instruments=instruments),
                action,
            )

    return failure(detail=f"Unknown market-data action: {action}")


def dispatch_auth(config: SkillConfig) -> int:
    """Run interactive 2FA authentication flow.

    Uses longer timeout (300s) so user has time to approve in Webull app.
    Returns exit code directly (not OperationResult) since this is interactive.
    """
    from webull_skill.sdk_client import (
        DeviceNotRegisteredError,
        SDKClient,
        TwoFactorAuthRequiredError,
    )

    print(f"Webull OpenAPI Authentication")
    print(f"{'=' * 40}")
    print(f"Region: {config.region_id.upper()}")
    print(f"Environment: {config.environment.upper()}")
    print(f"\nInitiating authentication...")
    print(f"If 2FA is required, please approve the request in your Webull app.")
    print(f"Waiting for approval (up to 5 minutes)...\n")

    sdk = SDKClient(config)
    try:
        sdk.initialize(interactive=True)
        print("Authentication successful!")
        return 0
    except DeviceNotRegisteredError as e:
        print(f"\n{e}", file=sys.stderr)
        return 1
    except TwoFactorAuthRequiredError as e:
        print(f"\n{e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nAuthentication failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """CLI main entry point.

    Output: tool functions return formatted text (with disclaimer) — printed
    directly to stdout, matching MCP's output style. Errors go to stderr.
    """
    parser = build_parser()
    args = parser.parse_args()

    if not args.module:
        parser.print_help()
        return 1

    set_sdk_logging(args.verbose_sdk_log)

    try:
        config = load_config(args.env_file)
        validate_config(config)

        # Set region-aware disclaimer at startup
        set_disclaimer_region(config.region_id)

        # Initialize audit logger
        audit = AuditLogger(config.audit_log_file)

        if args.module == "auth":
            return dispatch_auth(config)
        elif args.module == "trading":
            output = dispatch_trading(args, config)
        elif args.module == "market-data":
            output = dispatch_market_data(args, config)
        else:
            print(f"Unknown module: {args.module}", file=sys.stderr)
            return 1

        # output is either a formatted string (success) or an OperationResult (error)
        if isinstance(output, OperationResult):
            # Error case — print detail to stderr
            print(output.detail, file=sys.stderr)
            return 1
        else:
            # Success — print formatted text directly to stdout
            print(output)
            return 0

    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
