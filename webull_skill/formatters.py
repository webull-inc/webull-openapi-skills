"""Output formatting functions for Webull OpenAPI Skill.

Each function takes raw SDK response data (dict or list of dicts) and returns
a human-readable formatted string. The disclaimer prefix is region-aware:
- US: English only
- HK: English + Simplified Chinese + Traditional Chinese
- JP: English + Japanese
"""

from __future__ import annotations

from typing import Any

# Region-specific disclaimers
_DISCLAIMER_US = (
    "⚠️ Disclaimer: "
    "The information provided by this tool is for reference only "
    "and does not constitute investment advice. "
    "Trading involves risk; please make decisions carefully.\n\n"
)

_DISCLAIMER_HK = (
    "⚠️ Disclaimer: "
    "The information provided by this tool is for reference only "
    "and does not constitute investment advice. "
    "Trading involves risk; please make decisions carefully.\n"
    "本工具提供的信息仅供参考，不构成投资建议。交易有风险，请谨慎决策。\n"
    "本工具提供的資訊僅供參考，不構成投資建議。交易有風險，請謹慎決策。\n\n"
)

_DISCLAIMER_JP = (
    "⚠️ Disclaimer: "
    "The information provided by this tool is for reference only "
    "and does not constitute investment advice. "
    "Trading involves risk; please make decisions carefully.\n"
    "本ツールが提供する情報は参考目的のみであり、投資助言ではありません。"
    "取引にはリスクがあります。慎重に判断してください。\n\n"
)

# Default (backward compatibility)
DISCLAIMER = _DISCLAIMER_US

# Current region (set at startup)
_current_region: str = "us"


def set_disclaimer_region(region_id: str) -> None:
    """Set the region for disclaimer output. Called once at startup."""
    global _current_region, DISCLAIMER
    _current_region = region_id.lower()
    if _current_region == "hk":
        DISCLAIMER = _DISCLAIMER_HK
    elif _current_region == "jp":
        DISCLAIMER = _DISCLAIMER_JP
    else:
        # US, SG, TH, MY, UK, MX, BR — English only
        DISCLAIMER = _DISCLAIMER_US

_NO_DATA = "No data available."


def prepend_disclaimer(content: str) -> str:
    """Prepend the region-appropriate disclaimer to *content*."""
    return DISCLAIMER + content


def extract_response_data(response: Any) -> Any:
    """Extract JSON data from SDK response.

    The Webull SDK returns requests.Response objects from most API calls.
    This helper extracts the JSON data, handling both Response objects
    and already-parsed data (for backward compatibility).
    """
    if response is None:
        return None
    # If it's a requests.Response object, extract JSON
    if hasattr(response, 'json') and callable(response.json):
        try:
            return response.json()
        except Exception:
            if hasattr(response, 'content'):
                return response.content
            return response
    # Already parsed data (dict, list, etc.)
    return response


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get(d: dict, key: str, default: str = "N/A") -> str:
    """Safely get a value from *d*, returning *default* when missing/None."""
    val = d.get(key)
    if val is None:
        return default
    return str(val)


def _get_any(d: dict, keys: tuple[str, ...], default: str = "N/A") -> str:
    """Return the first present value among *keys*."""
    for key in keys:
        val = d.get(key)
        if val is not None:
            return str(val)
    return default


# ---------------------------------------------------------------------------
# Account formatters
# ---------------------------------------------------------------------------

def format_account_list(data: list[dict] | None) -> str:
    """Format account list response."""
    if not data:
        return _NO_DATA
    lines: list[str] = ["=== Account List ==="]
    for i, acct in enumerate(data, 1):
        lines.append(f"\n[{i}]")
        lines.append(f"  Account ID:      {_get(acct, 'account_id')}")
        lines.append(f"  Account Number:  {_get(acct, 'account_number')}")
        lines.append(f"  User ID:         {_get(acct, 'user_id')}")
        lines.append(f"  Account Type:    {_get(acct, 'account_type')}")
        lines.append(f"  Account Class:   {_get(acct, 'account_class')}")
        lines.append(f"  Account Label:   {_get(acct, 'account_label')}")
    return "\n".join(lines)


def format_account_balance(data: dict | None) -> str:
    """Format account balance response."""
    if not data:
        return _NO_DATA
    lines: list[str] = ["=== Account Balance ==="]

    # Top-level summary
    lines.append(f"  Currency:              {_get(data, 'total_asset_currency')}")
    lines.append(f"  Total Cash Balance:    {_get(data, 'total_cash_balance')}")
    lines.append(f"  Total Market Value:    {_get(data, 'total_market_value')}")
    lines.append(f"  Total Unrealized P&L:  {_get(data, 'total_unrealized_profit_loss')}")

    # US-specific fields
    if data.get("total_net_liquidation_value"):
        lines.append(f"  Net Liquidation:       {_get(data, 'total_net_liquidation_value')}")
    if data.get("total_day_profit_loss"):
        lines.append(f"  Day P&L:               {_get(data, 'total_day_profit_loss')}")
    if data.get("day_trades_left"):
        lines.append(f"  Day Trades Left:       {_get(data, 'day_trades_left')}")

    # Per-currency breakdown
    currency_assets = data.get("account_currency_assets", [])
    for asset in currency_assets:
        currency = _get(asset, "currency")
        lines.append(f"\n  --- {currency} ---")
        lines.append(f"  Cash Balance:          {_get(asset, 'cash_balance')}")
        lines.append(f"  Settled Cash:          {_get(asset, 'settled_cash')}")
        lines.append(f"  Unsettled Cash:        {_get(asset, 'unsettled_cash')}")
        lines.append(f"  Market Value:          {_get(asset, 'market_value')}")
        lines.append(f"  Buying Power:          {_get(asset, 'buying_power')}")
        lines.append(f"  Unrealized P&L:        {_get(asset, 'unrealized_profit_loss')}")
        lines.append(f"  Available Withdrawal:  {_get(asset, 'available_withdrawal')}")
        if asset.get("option_buying_power"):
            lines.append(f"  Option Buying Power:   {_get(asset, 'option_buying_power')}")
        if asset.get("day_buying_power"):
            lines.append(f"  Day Buying Power:      {_get(asset, 'day_buying_power')}")

    return "\n".join(lines)


def format_positions(data: list[dict] | None) -> str:
    """Format account positions response."""
    if isinstance(data, dict):
        data = (
            data.get("positions")
            or data.get("holdings")
            or data.get("items")
            or data.get("result")
            or [data]
        )
    if not data:
        return _NO_DATA
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Positions ==="]
    for i, pos in enumerate(data, 1):
        if not isinstance(pos, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Symbol:          {_get(pos, 'symbol')}")
        lines.append(f"  Instrument ID:   {_get_any(pos, ('instrument_id', 'ticker_id'))}")
        lines.append(f"  Quantity:        {_get_any(pos, ('quantity', 'qty'))}")
        lines.append(f"  Type:            {_get(pos, 'instrument_type')}")
        lines.append(f"  Cost Price:      {_get_any(pos, ('cost_price', 'cost_basis', 'avg_cost'))}")
        lines.append(f"  Last Price:      {_get(pos, 'last_price')}")
        lines.append(f"  Unrealized P&L:  {_get(pos, 'unrealized_profit_loss')}")
        lines.append(f"  Currency:        {_get(pos, 'currency')}")
        if pos.get("account_tax_type"):
            lines.append(f"  Account Tax Type:{_get(pos, 'account_tax_type')}")
        if pos.get("margin_type"):
            lines.append(f"  Margin Type:     {_get(pos, 'margin_type')}")
        if pos.get("position_intent"):
            lines.append(f"  Position Intent: {_get(pos, 'position_intent')}")
        legs = pos.get("legs", [])
        if legs:
            lines.append("  [Option Legs]")
            for j, leg in enumerate(legs, 1):
                lines.append(f"    Leg {j}:")
                lines.append(f"      Symbol:      {_get(leg, 'symbol')}")
                lines.append(f"      Quantity:    {_get(leg, 'quantity')}")
                lines.append(f"      Type:        {_get(leg, 'option_type')}")
                lines.append(f"      Strike:      {_get(leg, 'option_exercise_price')}")
                lines.append(f"      Expiry:      {_get(leg, 'option_expire_date')}")
    return "\n".join(lines)


def format_position_details(data: list[dict] | dict | None) -> str:
    """Format JP account position details response."""
    if not data:
        return _NO_DATA

    if isinstance(data, dict):
        items = None
        for key in ("items", "positions", "position_details", "data"):
            if key in data:
                items = data[key]
                break
        data = [data] if items is None else items

    if not isinstance(data, list) or not data:
        return _NO_DATA

    lines: list[str] = ["=== Position Details ==="]
    for i, detail in enumerate(data, 1):
        if not isinstance(detail, dict):
            continue
        lines.append(f"\n[Position Detail {i}]")
        lines.append(
            f"  {_get(detail, 'symbol'):>8s}  "
            f"Qty: {_get(detail, 'quantity'):>8s}  "
            f"Hold: {_get(detail, 'hold_type'):>6s}  "
            f"Market Value: {_get(detail, 'market_value'):>10s}  "
            f"Currency: {_get(detail, 'currency')}"
        )
        lines.append(
            f"{'':>10s}  "
            f"Name: {_get(detail, 'symbol_name')}  "
            f"Exchange: {_get(detail, 'exchange_code')}"
        )
        lines.append(
            f"{'':>10s}  "
            f"Average Price: {_get(detail, 'average_price'):>10s}  "
            f"Unrealized P&L: {_get(detail, 'unrealized_pl'):>10s}"
        )
        lines.append(
            f"{'':>10s}  "
            f"Account Tax Type: {_get(detail, 'account_tax_type')}  "
            f"Margin Type: {_get(detail, 'margin_type')}"
        )
        lines.append(
            f"{'':>10s}  "
            f"Instrument ID: {_get(detail, 'instrument_id')}  "
            f"Contract ID: {_get(detail, 'contract_id')}  "
            f"Position ID: {_get(detail, 'id')}"
        )
        lines.append(
            f"{'':>10s}  "
            f"Base Currency: {_get(detail, 'base_currency')}  "
            f"FX Rate: {_get(detail, 'fx_rate')}  "
            f"Base Currency Market Value: {_get(detail, 'base_currency_market_value')}"
        )

    if len(lines) == 1:
        return _NO_DATA
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Stock market data formatters
# ---------------------------------------------------------------------------

def format_stock_snapshot(data: list[dict] | None) -> str:
    """Format stock snapshot response."""
    if not data:
        return _NO_DATA
    lines: list[str] = []
    for snap in data:
        symbol = _get(snap, 'symbol')
        lines.append(f"=== Stock Snapshot: {symbol} ===")
        lines.append(f"  Symbol:          {symbol}")
        lines.append(f"  Price:           {_get(snap, 'price')}")
        lines.append(f"  Pre Close:       {_get(snap, 'pre_close')}")
        lines.append(f"  Change:          {_get(snap, 'change')}")
        lines.append(f"  Change %:        {_get(snap, 'change_ratio')}")
        lines.append(f"  Open:            {_get(snap, 'open')}")
        lines.append(f"  High:            {_get(snap, 'high')}")
        lines.append(f"  Low:             {_get(snap, 'low')}")
        lines.append(f"  Close:           {_get(snap, 'close')}")
        lines.append(f"  Volume:          {_get(snap, 'volume')}")
        lines.append(f"  Bid:             {_get(snap, 'bid')} x {_get(snap, 'bid_size')}")
        lines.append(f"  Ask:             {_get(snap, 'ask')} x {_get(snap, 'ask_size')}")
        if snap.get("extend_hour_last_price"):
            lines.append("")
            lines.append("  [Extended Hours]")
            lines.append(f"  Ext Price:       {_get(snap, 'extend_hour_last_price')}")
            lines.append(f"  Ext High:        {_get(snap, 'extend_hour_high')}")
            lines.append(f"  Ext Low:         {_get(snap, 'extend_hour_low')}")
            lines.append(f"  Ext Change:      {_get(snap, 'extend_hour_change')}")
            lines.append(f"  Ext Change %:    {_get(snap, 'extend_hour_change_ratio')}")
            lines.append(f"  Ext Volume:      {_get(snap, 'extend_hour_volume')}")
        if snap.get("ovn_price"):
            lines.append("")
            lines.append("  [Overnight]")
            lines.append(f"  OVN Price:       {_get(snap, 'ovn_price')}")
            lines.append(f"  OVN High:        {_get(snap, 'ovn_high')}")
            lines.append(f"  OVN Low:         {_get(snap, 'ovn_low')}")
            lines.append(f"  OVN Change:      {_get(snap, 'ovn_change')}")
            lines.append(f"  OVN Change %:    {_get(snap, 'ovn_change_ratio')}")
            lines.append(f"  OVN Volume:      {_get(snap, 'ovn_volume')}")
            lines.append(f"  OVN Bid:         {_get(snap, 'ovn_bid')} x {_get(snap, 'ovn_bid_size')}")
            lines.append(f"  OVN Ask:         {_get(snap, 'ovn_ask')} x {_get(snap, 'ovn_ask_size')}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_stock_quotes(data: Any) -> str:
    """Format stock quotes (bid/ask depth) response."""
    if not data:
        return _NO_DATA

    if isinstance(data, dict):
        symbol = _get(data, "symbol")
        quote_time = _get(data, "quote_time")
        lines: list[str] = [f"=== Stock Quotes: {symbol} ==="]
        if quote_time != "N/A":
            lines.append(f"  Quote Time:      {quote_time}")

        bids = data.get("bids", [])
        asks = data.get("asks", [])

        lines.append("")
        lines.append("  Bids:")
        for i, bid in enumerate(bids):
            lines.append(f"    L{i + 1}:  {_get(bid, 'price')} x {_get(bid, 'size')}")

        lines.append("")
        lines.append("  Asks:")
        for i, ask in enumerate(asks):
            lines.append(f"    L{i + 1}:  {_get(ask, 'price')} x {_get(ask, 'size')}")

        return "\n".join(lines)

    if isinstance(data, list):
        lines = ["=== Stock Quotes ==="]
        for q in data:
            if isinstance(q, dict):
                symbol = _get(q, 'symbol')
                lines.append(f"\n=== Stock Quotes: {symbol} ===")
                lines.append(f"  Bid:             {_get(q, 'bid')} x {_get(q, 'bid_size')}")
                lines.append(f"  Ask:             {_get(q, 'ask')} x {_get(q, 'ask_size')}")
        return "\n".join(lines)

    return _NO_DATA


# ---------------------------------------------------------------------------
# Bar helpers (shared across stock, crypto, futures, event)
# ---------------------------------------------------------------------------

_BAR_HEADER = (
    f"  {'Time':<22s}"
    f"{'Open':>12s}"
    f"{'High':>12s}"
    f"{'Low':>12s}"
    f"{'Close':>12s}"
    f"{'Volume':>14s}"
)


def _format_bar_row(bar: dict) -> str:
    """Format a single OHLCV bar as a table row."""
    return (
        f"  {_get(bar, 'time'):<22s}"
        f"{_get(bar, 'open'):>12s}"
        f"{_get(bar, 'high'):>12s}"
        f"{_get(bar, 'low'):>12s}"
        f"{_get(bar, 'close'):>12s}"
        f"{_get(bar, 'volume'):>14s}"
    )


def _unwrap_bars_envelope(data: Any) -> Any:
    """Unwrap top-level {result: [...]} envelope if present."""
    if not data:
        return None
    if isinstance(data, dict) and "result" in data:
        data = data["result"]
    return data or None


def _is_grouped_bars(data: Any) -> bool:
    """Check if data is grouped bars format [{symbol, result: [bars]}]."""
    return isinstance(data, list) and bool(data) and isinstance(data[0], dict) and "result" in data[0]


def _append_grouped_bars(lines: list[str], data: list[dict]) -> None:
    """Append grouped bars (batch format) to lines."""
    for group in data:
        symbol = _get(group, "symbol")
        if symbol != "N/A":
            lines.append(f"  --- {symbol} ---")
        lines.append(_BAR_HEADER)
        for bar in group.get("result", []):
            lines.append(_format_bar_row(bar))
        lines.append("")


def _append_flat_bars(lines: list[str], data: Any) -> None:
    """Append flat bars to lines."""
    lines.append(_BAR_HEADER)
    for bar in (data if isinstance(data, list) else []):
        if not isinstance(bar, dict):
            continue
        lines.append(_format_bar_row(bar))


def _format_bars_data(data: Any, title: str) -> str:
    """Shared formatter for OHLCV bar data across all asset types."""
    data = _unwrap_bars_envelope(data)
    if not data:
        return _NO_DATA

    lines: list[str] = [f"=== {title} ==="]

    if _is_grouped_bars(data):
        _append_grouped_bars(lines, data)
    else:
        _append_flat_bars(lines, data)

    return "\n".join(lines).rstrip()


def format_stock_bars(data: Any) -> str:
    """Format stock OHLCV bar data."""
    return _format_bars_data(data, "Stock Bars (OHLCV)")


# ---------------------------------------------------------------------------
# Tick helpers (shared across stock, futures, event)
# ---------------------------------------------------------------------------

_TICK_HEADER_FULL = (
    f"  {'Time':<22s}"
    f"{'Price':>12s}"
    f"{'Volume':>10s}"
    f"{'Side':>8s}"
    f"{'Session':>10s}"
)

_TICK_HEADER_SHORT = (
    f"  {'Time':<22s}"
    f"{'Price':>12s}"
    f"{'Volume':>10s}"
)


def _format_tick_row_full(tick: dict) -> str:
    """Format a single tick row with side and session."""
    return (
        f"  {_get(tick, 'time'):<22s}"
        f"{_get(tick, 'price'):>12s}"
        f"{_get(tick, 'volume'):>10s}"
        f"{_get(tick, 'side'):>8s}"
        f"{_get(tick, 'trading_session'):>10s}"
    )


def _format_tick_row_short(tick: dict) -> str:
    """Format a single tick row (price + volume only)."""
    return (
        f"  {_get(tick, 'time'):<22s}"
        f"{_get(tick, 'price'):>12s}"
        f"{_get(tick, 'volume'):>10s}"
    )


def _format_tick_row_side(tick: dict) -> str:
    """Format a single tick row with side (no session)."""
    return (
        f"  {_get(tick, 'time'):<22s}"
        f"{_get(tick, 'price'):>12s}"
        f"{_get(tick, 'volume'):>10s}"
        f"{_get(tick, 'side'):>8s}"
    )

_TICK_HEADER_SIDE = (
    f"  {'Time':<22s}"
    f"{'Price':>12s}"
    f"{'Volume':>10s}"
    f"{'Side':>8s}"
)


def format_stock_tick(data: Any) -> str:
    """Format stock tick-by-tick data."""
    if not data:
        return _NO_DATA

    if isinstance(data, dict):
        symbol = _get(data, "symbol")
        ticks = data.get("result", [])
        lines: list[str] = [f"=== Stock Ticks: {symbol} ==="]
        lines.append(_TICK_HEADER_FULL)
        for tick in ticks:
            lines.append(_format_tick_row_full(tick))
        return "\n".join(lines)

    lines = ["=== Stock Ticks ==="]
    lines.append(_TICK_HEADER_SHORT)
    for tick in data:
        lines.append(_format_tick_row_short(tick))
    return "\n".join(lines)


def format_stock_footprint(data: Any) -> str:
    """Format stock footprint (large order) data."""
    if not data:
        return _NO_DATA

    if isinstance(data, dict):
        data = [data]

    lines: list[str] = ["=== Stock Footprint ==="]
    for group in data:
        if isinstance(group, dict) and "result" in group:
            symbol = _get(group, "symbol")
            if symbol != "N/A":
                lines.append(f"  --- {symbol} ---")
            for fp in group.get("result", []):
                lines.append(f"  Time:            {_get(fp, 'time')}")
                lines.append(f"  Session:         {_get(fp, 'trading_session')}")
                lines.append(f"  Total:           {_get(fp, 'total')}")
                lines.append(f"  Delta:           {_get(fp, 'delta')}")
                lines.append(f"  Buy Total:       {_get(fp, 'buy_total')}")
                lines.append(f"  Sell Total:      {_get(fp, 'sell_total')}")
                lines.append("")
        else:
            lines.append(f"  Time:            {_get(group, 'time')}")
            lines.append(f"  Total:           {_get(group, 'total')}")
            lines.append(f"  Delta:           {_get(group, 'delta')}")
            lines.append("")
    return "\n".join(lines).rstrip()


# ---------------------------------------------------------------------------
# Crypto market data formatters
# ---------------------------------------------------------------------------

def format_crypto_snapshot(data: Any) -> str:
    """Format crypto snapshot response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        data = [data]
    lines: list[str] = []
    for snap in data:
        symbol = _get(snap, 'symbol')
        lines.append(f"=== Crypto Snapshot: {symbol} ===")
        lines.append(f"  Symbol:          {symbol}")
        lines.append(f"  Price:           {_get(snap, 'price')}")
        lines.append(f"  Pre Close:       {_get(snap, 'pre_close')}")
        lines.append(f"  Change:          {_get(snap, 'change')}")
        lines.append(f"  Change %:        {_get(snap, 'change_ratio')}")
        lines.append(f"  Open:            {_get(snap, 'open')}")
        lines.append(f"  High:            {_get(snap, 'high')}")
        lines.append(f"  Low:             {_get(snap, 'low')}")
        lines.append(f"  Bid:             {_get(snap, 'bid')} x {_get(snap, 'bid_size')}")
        lines.append(f"  Ask:             {_get(snap, 'ask')} x {_get(snap, 'ask_size')}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_crypto_bars(data: Any) -> str:
    """Format crypto OHLCV bar data."""
    return _format_bars_data(data, "Crypto Bars (OHLCV)")


# ---------------------------------------------------------------------------
# Futures market data formatters
# ---------------------------------------------------------------------------

def format_futures_tick(data: Any) -> str:
    """Format futures tick-by-tick data."""
    if not data:
        return _NO_DATA

    if isinstance(data, dict):
        symbol = _get(data, "symbol")
        ticks = data.get("result", [])
        lines: list[str] = [f"=== Futures Ticks: {symbol} ==="]
        lines.append(_TICK_HEADER_SIDE)
        for tick in ticks:
            lines.append(_format_tick_row_side(tick))
        return "\n".join(lines)

    lines = ["=== Futures Ticks ==="]
    lines.append(_TICK_HEADER_SHORT)
    for tick in data:
        lines.append(_format_tick_row_short(tick))
    return "\n".join(lines)


def format_futures_snapshot(data: Any) -> str:
    """Format futures snapshot response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        data = [data]
    lines: list[str] = []
    for snap in data:
        symbol = _get(snap, 'symbol')
        lines.append(f"=== Futures Snapshot: {symbol} ===")
        lines.append(f"  Symbol:          {symbol}")
        lines.append(f"  Price:           {_get(snap, 'price')}")
        lines.append(f"  Pre Close:       {_get(snap, 'pre_close')}")
        lines.append(f"  Change:          {_get(snap, 'change')}")
        lines.append(f"  Change %:        {_get(snap, 'change_ratio')}")
        lines.append(f"  Open:            {_get(snap, 'open')}")
        lines.append(f"  High:            {_get(snap, 'high')}")
        lines.append(f"  Low:             {_get(snap, 'low')}")
        lines.append(f"  Volume:          {_get(snap, 'volume')}")
        lines.append(f"  Open Interest:   {_get(snap, 'open_interest')}")
        lines.append(f"  Bid:             {_get(snap, 'bid')} x {_get(snap, 'bid_size')}")
        lines.append(f"  Ask:             {_get(snap, 'ask')} x {_get(snap, 'ask_size')}")
        lines.append(f"  Settle Price:    {_get(snap, 'settle_price')}")
        lines.append(f"  Settle Date:     {_get(snap, 'settle_date')}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_futures_depth(data: Any) -> str:
    """Format futures order book depth response."""
    if not data:
        return _NO_DATA
    if not isinstance(data, dict):
        return _NO_DATA

    symbol = _get(data, 'symbol')
    lines: list[str] = [f"=== Futures Depth: {symbol} ==="]

    bids = data.get("bids") or []
    asks = data.get("asks") or []

    lines.append("")
    lines.append("  Bids:")
    for i, bid in enumerate(bids):
        lines.append(f"    L{i + 1}:  {_get(bid, 'price')} x {_get(bid, 'size')}")

    lines.append("")
    lines.append("  Asks:")
    for i, ask in enumerate(asks):
        lines.append(f"    L{i + 1}:  {_get(ask, 'price')} x {_get(ask, 'size')}")

    return "\n".join(lines)


def format_futures_bars(data: Any) -> str:
    """Format futures OHLCV bar data."""
    return _format_bars_data(data, "Futures Bars (OHLCV)")


def format_futures_footprint(data: Any) -> str:
    """Format futures footprint (large order) data."""
    if not data:
        return _NO_DATA

    if isinstance(data, dict):
        data = [data]

    lines: list[str] = ["=== Futures Footprint ==="]
    for group in data:
        if isinstance(group, dict) and "result" in group:
            symbol = _get(group, "symbol")
            if symbol != "N/A":
                lines.append(f"  --- {symbol} ---")
            for fp in group.get("result", []):
                lines.append(f"  Time:            {_get(fp, 'time')}")
                lines.append(f"  Session:         {_get(fp, 'trading_session')}")
                lines.append(f"  Total:           {_get(fp, 'total')}")
                lines.append(f"  Delta:           {_get(fp, 'delta')}")
                lines.append(f"  Buy Total:       {_get(fp, 'buy_total')}")
                lines.append(f"  Sell Total:      {_get(fp, 'sell_total')}")
                lines.append("")
        else:
            lines.append(f"  Time:            {_get(group, 'time')}")
            lines.append(f"  Total:           {_get(group, 'total')}")
            lines.append(f"  Delta:           {_get(group, 'delta')}")
            lines.append("")
    return "\n".join(lines).rstrip()


# ---------------------------------------------------------------------------
# Event contract market data formatters
# ---------------------------------------------------------------------------

def format_event_tick(data: Any) -> str:
    """Format event contract tick-by-tick data."""
    if not data:
        return _NO_DATA

    if isinstance(data, dict):
        symbol = _get(data, "symbol")
        ticks = data.get("result", [])
        lines: list[str] = [f"=== Event Ticks: {symbol} ==="]
        lines.append(_TICK_HEADER_SIDE)
        for tick in ticks:
            lines.append(_format_tick_row_side(tick))
        return "\n".join(lines)

    lines = ["=== Event Ticks ==="]
    lines.append(_TICK_HEADER_SHORT)
    for tick in data:
        lines.append(_format_tick_row_short(tick))
    return "\n".join(lines)


def format_event_snapshot(data: Any) -> str:
    """Format event contract snapshot response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        data = [data]
    lines: list[str] = []
    for snap in data:
        symbol = _get(snap, 'symbol')
        lines.append(f"=== Event Snapshot: {symbol} ===")
        lines.append(f"  Symbol:          {symbol}")
        lines.append(f"  Price:           {_get(snap, 'price')}")
        lines.append(f"  Change:          {_get(snap, 'change')}")
        lines.append(f"  Change %:        {_get(snap, 'change_ratio')}")
        lines.append(f"  Volume:          {_get(snap, 'volume')}")
        lines.append(f"  Bid:             {_get(snap, 'bid')} x {_get(snap, 'bid_size')}")
        lines.append(f"  Ask:             {_get(snap, 'ask')} x {_get(snap, 'ask_size')}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_event_depth(data: Any) -> str:
    """Format event contract order book depth."""
    if not data:
        return _NO_DATA
    if not isinstance(data, dict):
        return _NO_DATA

    symbol = _get(data, 'symbol')
    lines: list[str] = [f"=== Event Depth: {symbol} ==="]

    bids = data.get("bids") or []
    asks = data.get("asks") or []

    lines.append("")
    lines.append("  Bids:")
    for i, bid in enumerate(bids):
        lines.append(f"    L{i + 1}:  {_get(bid, 'price')} x {_get(bid, 'size')}")

    lines.append("")
    lines.append("  Asks:")
    for i, ask in enumerate(asks):
        lines.append(f"    L{i + 1}:  {_get(ask, 'price')} x {_get(ask, 'size')}")

    return "\n".join(lines)


def format_event_bars(data: Any) -> str:
    """Format event contract OHLCV bar data."""
    return _format_bars_data(data, "Event Bars (OHLCV)")


# ---------------------------------------------------------------------------
# Order formatters
# ---------------------------------------------------------------------------

def _format_order_detail(detail: dict) -> list[str]:
    """Format the core fields of a single order detail."""
    return [
        f"    Client Order ID:     {_get(detail, 'client_order_id')}",
        f"    Order ID:            {_get(detail, 'order_id')}",
        f"    Symbol:              {_get(detail, 'symbol')}",
        f"    Market:              {_get(detail, 'market')}",
        f"    Side:                {_get(detail, 'side')}",
        f"    Status:              {_get(detail, 'status')}",
        f"    Order Type:          {_get(detail, 'order_type')}",
        f"    Instrument Type:     {_get(detail, 'instrument_type')}",
        f"    Quantity:            {_get_any(detail, ('quantity', 'qty'))}",
        f"    Total Quantity:      {_get(detail, 'total_quantity')}",
        f"    Filled Quantity:     {_get(detail, 'filled_quantity')}",
        f"    Limit Price:         {_get(detail, 'limit_price')}",
        f"    Stop Price:          {_get(detail, 'stop_price')}",
        f"    Filled Price:        {_get(detail, 'filled_price')}",
        f"    Time In Force:       {_get(detail, 'time_in_force')}",
        f"    Trading Session:     {_get(detail, 'support_trading_session')}",
        f"    Place Time:          {_get(detail, 'place_time_at')}",
        f"    Place Timestamp:     {_get(detail, 'place_time')}",
        f"    Filled Time:         {_get(detail, 'filled_time_at')}",
        f"    Filled Timestamp:    {_get(detail, 'filled_time')}",
    ]


def _format_order_extra_fields(detail: dict) -> list[str]:
    """Format optional trailing, algo, event, and JP stock fields."""
    lines: list[str] = []

    if detail.get("trailing_type"):
        lines.append(f"    Trailing Type:       {_get(detail, 'trailing_type')}")
        lines.append(f"    Trailing Step:       {_get(detail, 'trailing_stop_step')}")

    if detail.get("algo_type"):
        lines.append(f"    Algo Type:           {_get(detail, 'algo_type')}")
        if detail.get("algo_start_time"):
            lines.append(f"    Algo Start Time:     {_get(detail, 'algo_start_time')}")
        if detail.get("algo_end_time"):
            lines.append(f"    Algo End Time:       {_get(detail, 'algo_end_time')}")
        if detail.get("target_vol_percent"):
            lines.append(f"    Target Vol %:        {_get(detail, 'target_vol_percent')}")
        if detail.get("max_target_percent"):
            lines.append(f"    Max Target %:        {_get(detail, 'max_target_percent')}")

    if detail.get("event_outcome"):
        lines.append(f"    Event Outcome:       {_get(detail, 'event_outcome')}")

    if detail.get("account_tax_type"):
        lines.append(f"    Account Tax Type:    {_get(detail, 'account_tax_type')}")

    if detail.get("margin_type"):
        lines.append(f"    Margin Type:         {_get(detail, 'margin_type')}")

    if detail.get("position_intent"):
        lines.append(f"    Position Intent:     {_get(detail, 'position_intent')}")

    close_contracts = detail.get("close_contracts")
    if close_contracts:
        if isinstance(close_contracts, list):
            lines.append("    Close Contracts:")
            for i, contract in enumerate(close_contracts, 1):
                if isinstance(contract, dict):
                    lines.append(f"      Contract {i}:")
                    lines.append(f"        Contract ID:     {_get(contract, 'contract_id')}")
                    lines.append(f"        Quantity:        {_get_any(contract, ('quantity', 'qty'))}")
                else:
                    lines.append(f"      Contract {i}:      {contract}")
        else:
            lines.append(f"    Close Contracts:     {close_contracts}")

    return lines


def _format_option_legs(legs: list[dict]) -> list[str]:
    """Format option legs for an order detail."""
    lines: list[str] = ["\n    [Option Legs]"]
    for j, leg in enumerate(legs, 1):
        lines.append(f"      Leg {j}:")
        lines.append(f"        Symbol:             {_get(leg, 'symbol')}")
        lines.append(f"        Side:               {_get(leg, 'side')}")
        lines.append(f"        Quantity:           {_get(leg, 'quantity')}")
        lines.append(f"        Option Type:        {_get(leg, 'option_type')}")
        lines.append(f"        Option Category:    {_get(leg, 'option_category')}")
        lines.append(f"        Option Strategy:    {_get(leg, 'option_strategy')}")
        lines.append(f"        Strike Price:       {_get(leg, 'strike_price')}")
        lines.append(f"        Expire Date:        {_get(leg, 'option_expire_date')}")
        lines.append(f"        Multiplier:         {_get(leg, 'option_contract_multiplier')}")
        lines.append(f"        Deliverable:        {_get(leg, 'option_contract_deliverable')}")
    return lines


def _format_order_item(data: dict) -> list[str]:
    """Format a single order item (used by history, open orders, and detail)."""
    lines: list[str] = [
        f"Client Order ID:  {_get(data, 'client_order_id')}",
        f"Combo Type:       {_get(data, 'combo_type')}",
    ]

    orders = data.get("orders", [])
    if not orders or not isinstance(orders, list):
        detail_keys = {
            "order_id", "symbol", "side", "status", "order_type",
            "account_tax_type", "margin_type", "position_intent", "close_contracts",
        }
        if detail_keys.intersection(data.keys()):
            lines.append("\n  [Order Details]")
            lines.extend(_format_order_detail(data))
            lines.extend(_format_order_extra_fields(data))
            return lines
        lines.append("\n  No order details available.")
        return lines

    for i, detail in enumerate(orders):
        header = f"\n  --- Order {i + 1} ---" if len(orders) > 1 else "\n  [Order Details]"
        lines.append(header)
        lines.extend(_format_order_detail(detail))
        lines.extend(_format_order_extra_fields(detail))
        legs = detail.get("legs") or []
        if legs:
            lines.extend(_format_option_legs(legs))

    return lines


def format_order_preview(data: dict | None) -> str:
    """Format order preview response."""
    if not data:
        return _NO_DATA
    lines: list[str] = ["=== Order Preview ==="]
    for key, value in data.items():
        label = key.replace("_", " ").title()
        lines.append(f"  {label}: {value}")
    return "\n".join(lines)


def format_order_history(data: list[dict] | None) -> str:
    """Format order history response."""
    if not data:
        return _NO_DATA
    lines: list[str] = ["=== Order History ==="]
    for i, order in enumerate(data, 1):
        lines.append(f"\n[Order Entry {i}]")
        lines.extend(_format_order_item(order))
    return "\n".join(lines)


def format_open_orders(data: list[dict] | None) -> str:
    """Format open orders response."""
    if not data:
        return _NO_DATA
    lines: list[str] = ["=== Open Orders ==="]
    for i, order in enumerate(data, 1):
        lines.append(f"\n[Order Entry {i}]")
        lines.extend(_format_order_item(order))
    return "\n".join(lines)


def format_order_detail(data: dict | None) -> str:
    """Format single order detail response."""
    if not data:
        return _NO_DATA
    lines: list[str] = ["=== Order Detail ==="]
    lines.extend(_format_order_item(data))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Instrument formatters
# ---------------------------------------------------------------------------

def _format_flat_item(item: dict, indent: str = "  ") -> list[str]:
    """Format a single dict item as flat key-value lines."""
    lines: list[str] = []
    for key, value in item.items():
        if isinstance(value, (dict, list)):
            continue
        lines.append(f"{indent}{key}: {value}")
    return lines


def _format_flat_list(data: Any, title: str) -> str:
    """Format a list of dicts as flat key-value output."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = [f"=== {title} ==="]
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        if i > 0:
            lines.append("")
        lines.extend(_format_flat_item(item))
    return "\n".join(lines)


def format_instruments(data: Any) -> str:
    """Format stock/ETF instrument list response."""
    return _format_flat_list(data, "Instruments")


def format_futures_products(data: Any) -> str:
    """Format futures products list."""
    return _format_flat_list(data, "Futures Products")


def format_futures_product_classes(data: Any) -> str:
    """Format futures product classification groups.

    Each item contains product_class_id and product_class_name.
    """
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return _NO_DATA

    lines: list[str] = ["=== Futures Product Classes ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Class ID:        {_get_any(item, ('product_class_id', 'class_id'))}")
        lines.append(f"  Class Name:      {_get_any(item, ('product_class_name', 'name'))}")
        # Some responses may include product_codes
        codes = item.get("product_codes")
        if isinstance(codes, list):
            lines.append(f"  Product Codes:   {', '.join(str(c) for c in codes)}")
    return "\n".join(lines)


def format_event_series(data: Any) -> str:
    """Format event series list."""
    return _format_flat_list(data, "Event Series")


def format_event_categories(data: Any) -> str:
    """Format event categories list."""
    return _format_flat_list(data, "Event Categories")


def format_event_events(data: Any) -> str:
    """Format event events list."""
    return _format_flat_list(data, "Event Events")


# ---------------------------------------------------------------------------
# Place / Replace order result formatters
# ---------------------------------------------------------------------------

def format_place_order_result(data: dict | None) -> str:
    """Format place-order result response."""
    if not data:
        return _NO_DATA
    lines: list[str] = [
        "=== Place Order Result ===",
        f"Client Order ID: {_get(data, 'client_order_id')}",
        f"Status:          {_get(data, 'status')}",
    ]
    return "\n".join(lines)


def format_replace_order_result(data: dict | None) -> str:
    """Format replace-order result response."""
    if not data:
        return _NO_DATA
    lines: list[str] = [
        "=== Replace Order Result ===",
        f"Client Order ID: {_get(data, 'client_order_id')}",
        f"Status:          {_get(data, 'status')}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# NOII formatters
# ---------------------------------------------------------------------------

def format_noii_bars(data: Any) -> str:
    """Format NOII (Net Order Imbalance Indicator) K-line data."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("result") or data.get("items") or [data]
    elif isinstance(data, list):
        items = data
    else:
        return _NO_DATA

    # Extract instrument_id and symbol from the first record for the title
    first = items[0] if items and isinstance(items[0], dict) else {}
    symbol = _get(first, "symbol")
    instrument_id = _get(first, "instrument_id")

    title = "=== NOII Bars"
    if symbol != "N/A":
        title += f": {symbol}"
    title += " ==="
    lines: list[str] = [title]
    lines.append(f"  Instrument ID:   {instrument_id}")
    lines.append(f"  Symbol:          {symbol}")
    lines.append("")
    header = (
        f"  {'Time':<22s}"
        f"{'Ref Price':>12s}"
        f"{'Near Price':>12s}"
        f"{'Far Price':>12s}"
        f"{'Action Type':>14s}"
    )
    lines.append(header)
    for bar in items:
        if not isinstance(bar, dict):
            continue
        lines.append(
            f"  {_get(bar, 'imbalance_time'):<22s}"
            f"{_get(bar, 'imbalance_ref_price'):>12s}"
            f"{_get(bar, 'imbalance_near_price'):>12s}"
            f"{_get(bar, 'imbalance_far_price'):>12s}"
            f"{_get(bar, 'imbalance_action_type'):>14s}"
        )
    return "\n".join(lines)


def format_noii_snapshot(data: Any) -> str:
    """Format NOII snapshot data."""
    if not data:
        return _NO_DATA
    if isinstance(data, list):
        data = data[0] if data else None
    if not isinstance(data, dict):
        return _NO_DATA

    lines: list[str] = [f"=== NOII Snapshot: {_get(data, 'symbol')} ==="]
    lines.append(f"  Instrument ID:       {_get(data, 'instrument_id')}")
    lines.append(f"  Symbol:              {_get(data, 'symbol')}")
    lines.append(f"  Imbalance Time:      {_get(data, 'imbalance_time')}")
    lines.append(f"  Action Type:         {_get(data, 'imbalance_action_type')}")
    lines.append(f"  Paired Shares:       {_get(data, 'paired_shares')}")
    lines.append(f"  Imbalance Shares:    {_get(data, 'imbalance_shares')}")
    lines.append(f"  Imbalance Side:      {_get(data, 'imbalance_side')}")
    lines.append(f"  Ref Price:           {_get(data, 'imbalance_ref_price')}")
    lines.append(f"  Near Price:          {_get(data, 'imbalance_near_price')}")
    lines.append(f"  Far Price:           {_get(data, 'imbalance_far_price')}")
    lines.append(f"  Var Indicator:       {_get(data, 'imbalance_var_indicator')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Screener formatters
# ---------------------------------------------------------------------------

def _format_screener_item(item: dict) -> list[str]:
    """Format a single screener result row."""
    return [
        f"  Instrument ID:   {_get(item, 'instrument_id')}",
        f"  Symbol:          {_get(item, 'symbol')}",
        f"  Name:            {_get(item, 'name')}",
        f"  Exchange:        {_get(item, 'exchange_code')}",
        f"  Currency:        {_get(item, 'currency_code')}",
        f"  Price:           {_get(item, 'price')}",
        f"  Pre Close:       {_get(item, 'pre_close')}",
        f"  Open:            {_get(item, 'open')}",
        f"  High:            {_get(item, 'high')}",
        f"  Low:             {_get(item, 'low')}",
        f"  Close:           {_get(item, 'close')}",
        f"  Change:          {_get(item, 'change')}",
        f"  Change Ratio:    {_get(item, 'change_ratio')}",
        f"  Volume:          {_get(item, 'volume')}",
        f"  Turnover:        {_get(item, 'turnover')}",
        f"  Turnover Rate:   {_get(item, 'turnover_rate')}",
        f"  Market Value:    {_get(item, 'market_value')}",
        f"  Amplitude:       {_get(item, 'amplitude')}",
    ]


def format_gainers_losers(data: Any) -> str:
    """Format gainers/losers screener response."""
    if not data:
        return _NO_DATA
    has_more: bool | None = None
    if isinstance(data, dict):
        has_more = data.get("has_more")
        items = data.get("data") or data.get("items") or data.get("result") or []
    elif isinstance(data, list):
        items = data
    else:
        return _NO_DATA
    if not items:
        return _NO_DATA

    lines: list[str] = ["=== Gainers / Losers ==="]
    for i, item in enumerate(items, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.extend(_format_screener_item(item))
    if has_more is not None:
        lines.append("")
        lines.append(f"  [Has More: {'Yes' if has_more else 'No'}]")
    return "\n".join(lines)


def format_most_active(data: Any) -> str:
    """Format most active screener response."""
    if not data:
        return _NO_DATA
    has_more: bool | None = None
    if isinstance(data, dict):
        has_more = data.get("has_more")
        items = data.get("data") or data.get("items") or data.get("result") or []
    elif isinstance(data, list):
        items = data
    else:
        return _NO_DATA
    if not items:
        return _NO_DATA

    lines: list[str] = ["=== Most Active ==="]
    for i, item in enumerate(items, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.extend(_format_screener_item(item))
        if item.get("relative_volume_10d"):
            lines.append(f"  Rel Vol 10D:     {_get(item, 'relative_volume_10d')}")
    if has_more is not None:
        lines.append("")
        lines.append(f"  [Has More: {'Yes' if has_more else 'No'}]")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Watchlist formatters
# ---------------------------------------------------------------------------

def format_watchlist(data: Any) -> str:
    """Format watchlist list response."""
    if not data:
        return _NO_DATA
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("items") or data.get("result") or [data]
    else:
        return _NO_DATA

    lines: list[str] = ["=== Watchlists ==="]
    for i, wl in enumerate(items, 1):
        if not isinstance(wl, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Watchlist ID:    {_get(wl, 'watchlist_id')}")
        lines.append(f"  Name:            {_get(wl, 'name')}")
        lines.append(f"  Sort:            {_get(wl, 'sort')}")
        lines.append(f"  Created:         {_get(wl, 'create_time')}")
        lines.append(f"  Updated:         {_get(wl, 'update_time')}")
    return "\n".join(lines)


def format_watchlist_instruments(data: Any) -> str:
    """Format watchlist instruments response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        wl_id = _get(data, "watchlist_id")
        items = data.get("items") or data.get("instruments") or []
    elif isinstance(data, list):
        wl_id = "N/A"
        items = data
    else:
        return _NO_DATA

    lines: list[str] = [f"=== Watchlist Instruments (ID: {wl_id}) ==="]
    for i, inst in enumerate(items, 1):
        if not isinstance(inst, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Instrument ID:   {_get(inst, 'instrument_id')}")
        lines.append(f"  Symbol:          {_get(inst, 'symbol')}")
        lines.append(f"  Name:            {_get(inst, 'name')}")
        lines.append(f"  Exchange:        {_get(inst, 'exchange_code')}")
        lines.append(f"  Sort:            {_get(inst, 'sort')}")
        lines.append(f"  Added Time:      {_get(inst, 'added_time')}")
    return "\n".join(lines)


def format_watchlist_result(data: Any, operation: str = "Watchlist Operation") -> str:
    """Format watchlist create/update/delete/add/remove result."""
    lines: list[str] = [f"=== {operation} ==="]
    if not data:
        lines.append("  Success")
        return "\n".join(lines)
    if isinstance(data, dict):
        if data.get("watchlist_id"):
            lines.append(f"  Watchlist ID:    {_get(data, 'watchlist_id')}")
        if data.get("success") is not None:
            lines.append(f"  Success:         {_get(data, 'success')}")
        if not data:
            lines.append("  Success")
    else:
        lines.append("  Success")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Company profile / Analyst formatters
# ---------------------------------------------------------------------------

def format_company_profile(data: Any) -> str:
    """Format company profile response."""
    if not data:
        return _NO_DATA
    if isinstance(data, list):
        data = data[0] if data else None
    if not isinstance(data, dict):
        return _NO_DATA

    lines: list[str] = [f"=== Company Profile: {_get(data, 'symbol')} ==="]
    lines.append(f"  Symbol:          {_get(data, 'symbol')}")
    lines.append(f"  Company Name:    {_get(data, 'company_name')}")
    lines.append(f"  Established:     {_get(data, 'establish_date')}")
    lines.append(f"  CEO:             {_get(data, 'ceo')}")
    lines.append(f"  Employees:       {_get(data, 'employees')}")
    lines.append(f"  Exchange:        {_get(data, 'exhibition_code')}")
    lines.append(f"  Address:         {_get(data, 'address')}")
    industries = data.get("industries")
    if industries and isinstance(industries, list):
        lines.append(f"  Industries:      {', '.join(str(i) for i in industries)}")
    desc = data.get("profile") or ""
    if desc:
        lines.append(f"\n  Description:")
        for chunk in [desc[i:i+100] for i in range(0, len(desc), 100)]:
            lines.append(f"    {chunk}")
    return "\n".join(lines)


def format_analyst_rating(data: Any) -> str:
    """Format analyst rating response."""
    if not data:
        return _NO_DATA
    if isinstance(data, list):
        data = data[0] if data else None
    if not isinstance(data, dict):
        return _NO_DATA

    lines: list[str] = [f"=== Analyst Rating: {_get(data, 'symbol')} ==="]
    lines.append(f"  Symbol:          {_get(data, 'symbol')}")
    lines.append(f"  Total Analysts:  {_get(data, 'number')}")
    lines.append(f"  Strong Buy:      {_get(data, 'strong_buy')}")
    lines.append(f"  Buy:             {_get(data, 'buy')}")
    lines.append(f"  Hold:            {_get(data, 'hold')}")
    lines.append(f"  Underperform:    {_get(data, 'under_perform')}")
    lines.append(f"  Sell:            {_get(data, 'sell')}")
    lines.append(f"  Effective Date:  {_get(data, 'effective_start_date')}")
    return "\n".join(lines)


def format_analyst_target_price(data: Any) -> str:
    """Format analyst target price response."""
    if not data:
        return _NO_DATA
    if isinstance(data, list):
        data = data[0] if data else None
    if not isinstance(data, dict):
        return _NO_DATA

    lines: list[str] = [f"=== Analyst Target Price: {_get(data, 'symbol')} ==="]
    lines.append(f"  Symbol:          {_get(data, 'symbol')}")
    lines.append(f"  Currency:        {_get(data, 'currency')}")
    lines.append(f"  Mean Target:     {_get(data, 'mean')}")
    lines.append(f"  Median Target:   {_get(data, 'median')}")
    lines.append(f"  High Target:     {_get(data, 'high')}")
    lines.append(f"  Low Target:      {_get(data, 'low')}")
    lines.append(f"  Effective Date:  {_get(data, 'effective_start_date')}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fundamentals data formatters
# ---------------------------------------------------------------------------

def format_capital_flow(data: Any) -> str:
    """Format capital flow distribution response."""
    return _format_generic_list(data, "Capital Flow")


def format_industry_comparison(data: Any) -> str:
    """Format industry comparison response."""
    if not data:
        return _NO_DATA
    sort_type = ""
    industry_name = ""
    if isinstance(data, dict):
        sort_type = data.get("type", "")
        industry_name = data.get("industry_name", "")
        items = data.get("data") or data.get("result") or data.get("items") or data.get("stocks")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Industry Comparison ==="]
    if industry_name:
        lines.append(f"  Industry:        {industry_name}")
    if sort_type:
        lines.append(f"  Sort By:         {sort_type}")
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Symbol:          {_get(item, 'symbol')}")
        lines.append(f"  Name:            {_get(item, 'name')}")
        lines.append(f"  Rank:            {_get(item, 'rank')}")
        lines.append(f"  Value:           {_get(item, 'value')}")
    return "\n".join(lines)


def format_sec_filings(data: Any) -> str:
    """Format SEC filings response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("filings") or data.get("data") or data.get("result") or data.get("items")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== SEC Filings ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Title:           {_get(item, 'title')}")
        lines.append(f"  Publish Date:    {_get(item, 'publish_date')}")
        url = item.get("url") or item.get("filing_url")
        if url:
            lines.append(f"  URL:             {url}")
    return "\n".join(lines)


def format_earnings_calendar(data: Any) -> str:
    """Format earnings calendar response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("data") or data.get("result") or data.get("items")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Earnings Calendar ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Fiscal Year:     {_get(item, 'fiscal_year')}")
        lines.append(f"  Fiscal Period:   {_get(item, 'fiscal_period')}")
        lines.append(f"  Publish Date:    {_get(item, 'expected_publish_date')}")
        lines.append(f"  Currency:        {_get(item, 'currency')}")
        lines.append(f"  EPS Estimate:    {_get(item, 'eps_est')}")
        lines.append(f"  EPS Actual:      {_get(item, 'eps_actual')}")
        lines.append(f"  Revenue Estimate:{_get(item, 'rev_est')}")
        lines.append(f"  Revenue Actual:  {_get(item, 'rev_actual')}")
    return "\n".join(lines)


def format_dividend_calendar(data: Any) -> str:
    """Format dividend calendar response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("data") or data.get("result") or data.get("items")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Dividend Calendar ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Ex-Dividend Date:{_get(item, 'ex_dividend_date')}")
        lines.append(f"  Record Date:     {_get(item, 'record_date')}")
        lines.append(f"  Pay Date:        {_get(item, 'pay_date')}")
        lines.append(f"  Amount:          {_get(item, 'amount')}")
        lines.append(f"  Currency:        {_get(item, 'currency')}")
    return "\n".join(lines)


def _format_generic_list(data: Any, title: str, key_candidates: tuple[str, ...] = ()) -> str:
    """Generic list formatter for screener/fund responses.

    Extracts items from a dict wrapper (trying key_candidates + common keys),
    then renders each item's key-value pairs.
    """
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = None
        for key in (*key_candidates, "data", "result", "items"):
            candidate = data.get(key)
            if candidate and isinstance(candidate, list):
                items = candidate
                break
        if items is not None:
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = [f"=== {title} ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        for k, v in item.items():
            if v is not None:
                lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def _format_financials_table(data: Any, title: str) -> str:
    """Generic formatter for financial statement data."""
    return _format_generic_list(data, title)


def format_financials_indicators(data: Any) -> str:
    """Format financials indicators response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict) and "values" in data:
        lines: list[str] = ["=== Financials Indicators ==="]
        currency = data.get("currency", "")
        if currency:
            lines.append(f"  Currency:        {currency}")
        values = data.get("values", {})
        for metric, records in values.items():
            lines.append(f"\n  --- {metric} ---")
            if isinstance(records, list):
                for rec in records:
                    if isinstance(rec, dict):
                        fy = rec.get("fiscal_year", "")
                        fp = rec.get("fiscal_period", "")
                        val = rec.get("value", "")
                        lines.append(f"    FY{fy} Q{fp}: {val}")
        return "\n".join(lines)
    return _format_financials_table(data, "Financials Indicators")


def format_financials_income(data: Any) -> str:
    """Format financials income statement response."""
    return _format_financials_table(data, "Financials Income Statement")


def format_financials_cashflow(data: Any) -> str:
    """Format financials cashflow statement response."""
    return _format_financials_table(data, "Financials Cashflow Statement")


def format_financials_balance_sheet(data: Any) -> str:
    """Format financials balance sheet response."""
    return _format_financials_table(data, "Financials Balance Sheet")


def format_financials_alert(data: Any) -> str:
    """Format financials alert response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        lines: list[str] = ["=== Financials Alert ==="]
        lines.append(f"  Fiscal Year:     {_get(data, 'fiscal_year')}")
        lines.append(f"  Fiscal Period:   {_get(data, 'fiscal_period')}")
        lines.append(f"  Start Date:      {_get(data, 'start_date')}")
        lines.append(f"  End Date:        {_get(data, 'end_date')}")
        lines.append(f"  Currency:        {_get(data, 'currency')}")
        lines.append(f"  EPS Estimate:    {_get(data, 'eps_est')}")
        lines.append(f"  EPS Last Year:   {_get(data, 'eps_ly')}")
        lines.append(f"  Revenue Estimate:{_get(data, 'rev_est')}")
        lines.append(f"  Revenue Last Year:{_get(data, 'rev_ly')}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = ["=== Financials Alert ==="]
        for i, item in enumerate(data, 1):
            if not isinstance(item, dict):
                continue
            lines.append(f"\n[{i}]")
            for k, v in item.items():
                if v is not None:
                    lines.append(f"  {k}: {v}")
        return "\n".join(lines)
    return _NO_DATA


def format_forecast_eps(data: Any) -> str:
    """Format forecast EPS response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("data") or data.get("result") or data.get("items")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Forecast EPS ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Fiscal Year:     {_get(item, 'fiscal_year')}")
        lines.append(f"  Fiscal Period:   {_get(item, 'fiscal_period')}")
        lines.append(f"  EPS Actual:      {_get(item, 'actual')}")
        lines.append(f"  EPS Estimate:    {_get(item, 'est')}")
        lines.append(f"  Reported:        {_get(item, 'reported')}")
    return "\n".join(lines)


def format_fund_brief(data: Any) -> str:
    """Format fund brief response."""
    if not data:
        return _NO_DATA
    if not isinstance(data, dict):
        return _NO_DATA
    lines: list[str] = [f"=== Fund Brief: {_get(data, 'symbol')} ==="]
    for k, v in data.items():
        if v is not None:
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def format_fund_allocation(data: Any) -> str:
    """Format fund allocation response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("data") or data.get("result") or data.get("items") or data.get("allocations")
        if items and isinstance(items, list):
            data_list = items
        else:
            lines = [f"=== Fund Allocation: {_get(data, 'symbol')} ==="]
            for k, v in data.items():
                if v is not None:
                    lines.append(f"  {k}: {v}")
            return "\n".join(lines)
    else:
        data_list = data if isinstance(data, list) else []
    lines = ["=== Fund Allocation ==="]
    for i, item in enumerate(data_list, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        for k, v in item.items():
            if v is not None:
                lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def format_fund_holdings(data: Any) -> str:
    """Format fund top holdings response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("data") or data.get("result") or data.get("items") or data.get("holdings")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Fund Holdings ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Symbol:          {_get(item, 'target_symbol')}")
        lines.append(f"  Name:            {_get(item, 'stock_name')}")
        lines.append(f"  Weight (%):      {_get(item, 'share_held_pct')}")
        lines.append(f"  Change (%):      {_get(item, 'share_held_chg_pct')}")
        lines.append(f"  Update Time:     {_get(item, 'update_time')}")
    return "\n".join(lines)


def format_fund_performance(data: Any) -> str:
    """Format fund performance response."""
    if not data:
        return _NO_DATA
    if not isinstance(data, dict):
        return _NO_DATA
    lines: list[str] = [f"=== Fund Performance: {_get(data, 'symbol')} ==="]
    for k, v in data.items():
        if v is not None:
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def format_fund_rating(data: Any) -> str:
    """Format fund rating response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Fund Rating ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Rating Agency:   {_get(item, 'rating_agency')}")
        lines.append(f"  Rating Date:     {_get(item, 'rating_date')}")
        lines.append(f"  Rating Cycle:    {_get(item, 'rating_cycle')}")
        lines.append(f"  Rating Results:  {_get(item, 'rating_results')}")
    return "\n".join(lines)


def format_fund_net_value(data: Any) -> str:
    """Format fund net value response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("data") or data.get("result") or data.get("items")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Fund Net Value ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Date:            {_get(item, 'date')}")
        lines.append(f"  Currency:        {_get(item, 'currency')}")
        lines.append(f"  Net Value:       {_get(item, 'net_value')}")
    return "\n".join(lines)


def format_fund_dividends(data: Any) -> str:
    """Format fund dividends response."""
    if not data:
        return _NO_DATA
    if isinstance(data, dict):
        items = data.get("data") or data.get("result") or data.get("items")
        if items and isinstance(items, list):
            data = items
        else:
            data = [data]
    if not isinstance(data, list):
        return _NO_DATA
    lines: list[str] = ["=== Fund Dividends ==="]
    for i, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue
        lines.append(f"\n[{i}]")
        lines.append(f"  Share Date:      {_get(item, 'share_date')}")
        lines.append(f"  Record Date:     {_get(item, 'record_date')}")
        lines.append(f"  Pay Date:        {_get(item, 'pay_date')}")
        lines.append(f"  DPS:             {_get(item, 'dps')}")
    return "\n".join(lines)


def format_fund_splits(data: Any) -> str:
    """Format fund splits response."""
    return _format_generic_list(data, "Fund Splits")


def format_fund_files(data: Any) -> str:
    """Format fund files response."""
    return _format_generic_list(data, "Fund Files")


# ---------------------------------------------------------------------------
# Screener: market sectors, high dividend, 52-week high/low
# ---------------------------------------------------------------------------

def format_market_sectors(data: Any) -> str:
    """Format market sectors overview response."""
    return _format_generic_list(data, "Market Sectors", key_candidates=("sectors",))


def format_market_sectors_detail(data: Any) -> str:
    """Format market sectors detail response."""
    return _format_generic_list(data, "Market Sectors Detail", key_candidates=("stocks",))


def format_high_dividend(data: Any) -> str:
    """Format high dividend rank list response."""
    return _format_generic_list(data, "High Dividend")


def format_52whl(data: Any) -> str:
    """Format 52-week high/low rank list response."""
    return _format_generic_list(data, "52-Week High/Low")
