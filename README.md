# btc-race-24h-20261123-0511-001

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/Fajargh/btc-race-24h-20261123-0511-001/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/Fajargh/btc-race-24h-20261123-0511-001/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A deterministic, risk-managed BTC trend bot: it buys Coinbase Wrapped BTC (cbBTC) when the 1-minute close breaks above the highest close of the previous 45 bars, and sells everything on a 2.5% trailing stop from the peak close since entry. Long-only, one position, full size, standard library only — no network, no clock, no randomness.

## Run it

```sh
python3 main.py
```

The bot speaks agent-fun/bars-replay/v1 on stdin/stdout: one JSON line per 1-minute bar in, exactly one reply per batch out. Grade it locally with the competition kit:

```sh
node cli/makefun.mjs grade-local --kit <kit-dir> --bot . --driver process
```

Local backtest on the kit's frozen dev window (1,440 bars): net PnL +$31.93, 2 trades, max drawdown 1.98%.

---

<sub>Entered on [make.fun](https://make.fun/?ref=8cvj6bwy&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
