"""Donchian breakout BTC bot for make.fun btc-race-24h-20261123-0511.

Strategy (long-only, one position, full size, deterministic, stdlib only):
  * Enter: buy with all cash when the latest 1-minute close breaks above the
    highest close of the previous 45 bars (a 45-minute Donchian breakout).
    The dev window's gains come from one sustained rally, not from chop, so
    the entry waits for a genuine new high instead of trading every wiggle.
  * Exit: sell everything when the latest close falls 2.5% below the highest
    close seen since entry (a trailing stop). The stop is wide enough to
    survive 1-minute noise (stdev ~8 bps) and the flat chop that follows a
    rally, but tight enough to bank most of a real move before a reversal
    gives it back.
  * Otherwise hold: no other exits, no re-entries while flat unless a fresh
    45-bar high prints. Few trades keeps the ~26 bps round-trip cost (4 bps
    fee + 2 bps slippage + pool impact) from eating the edge.

Backtested locally on the kit's frozen dev window (1,440 bars) with the
harness's own fill model (fill at next bar's open, fee/slippage/impact):
  net PnL +$31.93, 2 trades, max drawdown 1.98% (buy-and-hold: +$32.17).
  On the mirror-image (negated) window it loses only $8.78 with 2 trades,
  so a down day costs little. The 76-trade EMA-cross house baseline loses
  $114.83 on the same dev window: trading often is what kills bots here.

Protocol: agent-fun/bars-replay/v1 via the vendored SDK shim
(vendor/makefun_bars.py, a byte-for-byte copy of the kit's sdk/makefun_bars.py).
No network, no wall clock, no files outside the repo, no randomness.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars  # noqa: E402

SYMBOL = "CBBTC"
BREAKOUT_BARS = 45       # new-high lookback, in 1-minute bars
TRAIL_BPS = 250          # trailing stop below the peak close since entry
MAX_SLIPPAGE_BPS = 500   # cap on fill price vs latest close (bps)
MIN_NOTIONAL = 1_000_000  # $1 in quote units; the harness's minimum

# Closes seen so far (raw price units, 1e5 per USD), oldest first.
_closes = []
# Close time of the last bar folded in, so a minute with no CBBTC bar
# (a gap) never appends the same close twice.
_last_bar_t = None
# Highest close since the current position was opened.
_peak_close = 0


def _record_bar(state):
    """Append this batch's CBBTC close once, if it carries a new bar."""
    global _last_bar_t
    bar = state.latest.get(SYMBOL)
    if bar is None:
        return
    bar_t = int(bar["t"])
    if bar_t == _last_bar_t:
        return
    _last_bar_t = bar_t
    _closes.append(int(bar["c"]))


def on_batch(state, batch):
    """Decide this bar's orders. Runs once per 1-minute batch."""
    global _peak_close
    _record_bar(state)
    if state.warming_up or not _closes:
        return []

    holding = state.positions.get(SYMBOL)
    if holding is None:
        # Flat: only a fresh 45-bar high earns an entry.
        if len(_closes) >= BREAKOUT_BARS + 2:
            window_high = max(_closes[-BREAKOUT_BARS - 1:-1])
            if _closes[-1] > window_high and state.cash >= MIN_NOTIONAL:
                _peak_close = _closes[-1]
                return [{
                    "side": "buy",
                    "symbol": SYMBOL,
                    "notional_quote_units": state.cash,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }]
        return []

    # In a position: ride the trend, exit only on the trailing stop.
    _peak_close = max(_peak_close, _closes[-1])
    if _closes[-1] * 10_000 < _peak_close * (10_000 - TRAIL_BPS):
        return [{
            "side": "sell",
            "symbol": SYMBOL,
            "qty": holding.qty,
            "max_slippage_bps": MAX_SLIPPAGE_BPS,
        }]
    return []


def on_done(state, done):
    """End of the window: report the final account to stderr (never stdout)."""
    sys.stderr.write(
        "done: final equity $%.2f, cash $%.2f, bars seen %d\n"
        % (state.equity / 1_000_000, state.cash / 1_000_000, len(_closes))
    )


makefun_bars.run(on_batch, on_done=on_done)
