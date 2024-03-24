# Freqtrade

Be sure to check out the [Freqtrade] website and documentation for more information.

### Running

Once you have a strategy, running `docker compose up` in the parent directory will start Freqtrade in a dry run mode. In this `localhost:8080` is exposed with a UI to allow visualising activity.

### Getting Started

The first stage of testing or building a strategy is fetching data to work with. The following instructs Freqtrade to fetch 1H and 15m candle data for the last 180 days:

```
# `pairs` and `timeframes` are space separated
docker compose run --rm freqtrade download-data \
    --exchange binance \
    --pairs SUI/USDT SEI/USDT SOL/USDT NEAR/USDT ETH/USDT \
    --timeframes 1h 15m \
    --days 180
```

> NB: `--pairs` and `timeframes` are both space separated, and can contain additional values if you wish.

A new strategy can be created with the following:
```
docker compose run --rm freqtrade  new-strategy --strategy MyStrategy
```

Which you can then backtest with:
```
docker compose run --rm freqtrade backtesting --strategy MyStrategy
```

For most of the commands, [./config.json] will be used as a configuration source. Until deploying, the contains don't matter too much. The main parameters to be aware of are `stake_amount` and `dry_run_wallet` which set your trade size and wallet balance respectively, then `exchange` which determines which exchange to use.


### Optimising Strategies

Freqtrade has a built in optimisation tool which can be used to find the best parameters for a given strategy. This is done by running a backtest with a range of values for each parameter, and then selecting the best performing set. This is known as [Hyperopt | Freqtrade].

The primary requirement for this is exposing `parameters` in your strategy with a range of potential values:

```python
ema_fast = IntParameter(7, 15, default=12, space="buy")
ema_slow = IntParameter(26, 36, default=32, space="buy")
```

Freqtrade will then trial backtests for your strategy with different permuations of these values, and select the best performing set.

The following is an example of triggering this to run:
```
docker compose run --rm freqtrade hyperopt \
    --hyperopt-loss SharpeHyperOptLossDaily \
    --spaces buy roi stoploss trailing \
    --strategy MyStrategy \
    -e 300
```

> NB: This tuning requires a [Loss Functions | HyperOpt] to determine the strategy objective and ideal returns.



[./config.json]: ./config.json
[Freqtrade]: https://www.freqtrade.io/
[Hyperopt | Freqtrade]: https://www.freqtrade.io/en/stable/hyperopt/
[Loss Functions | HyperOpt]: https://www.freqtrade.io/en/stable/hyperopt/#loss-functions