import logging

import freqtrade.vendor.qtpylib.indicators as qtpylib
import pandas as pd
import talib.abstract as ta
from freqtrade.strategy import IntParameter, IStrategy
from pandas import DataFrame

logger = logging.getLogger(__name__)


class StochEMA(IStrategy):
    """
    Simple strategy to trade based on EMA positioning and StochRSI K & D crossovers.
    """

    timeframe = "1h"

    startup_candle_count = 50

    # NOTE: this strat only uses candle information, so processing between
    # new candles is a waste of resources as nothing will change
    process_only_new_candles = True

    ema_fast = IntParameter(7, 15, default=12, space="buy")
    ema_mid = IntParameter(15, 26, default=25, space="buy")
    ema_slow = IntParameter(26, 36, default=32, space="buy")
    stoch_k = IntParameter(3, 9, default=7, space="buy")
    stoch_d = IntParameter(3, 9, default=3, space="buy")
    rsi_length = IntParameter(9, 14, default=9, space="buy")
    stoch_length = IntParameter(9, 14, default=14, space="buy")

    minimal_roi = {
        "0": 1,
    }

    stoploss = -0.40

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, self.informative_timeframe) for pair in pairs]
        return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=self.ema_fast.value)
        dataframe["ema_mid"] = ta.EMA(dataframe, timeperiod=self.ema_mid.value)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=self.ema_slow.value)

        # StochRSI - https://github.com/freqtrade/freqtrade/issues/2961
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=self.rsi_length.value)
        period = self.stoch_length.value
        smooth_d = self.stoch_d.value
        smooth_k = self.stoch_k.value
        stochrsi = (dataframe["rsi"] - dataframe["rsi"].rolling(period).min()) / (
            dataframe["rsi"].rolling(period).max() - dataframe["rsi"].rolling(period).min()
        )
        dataframe["srsi_k"] = stochrsi.rolling(smooth_k).mean() * 100
        dataframe["srsi_d"] = dataframe["srsi_k"].rolling(smooth_d).mean()

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["ema_fast"] > dataframe["ema_mid"])
                & (dataframe["ema_mid"] > dataframe["ema_slow"])
                & qtpylib.crossed_above(dataframe["srsi_k"], dataframe["srsi_d"]),
            ),
            "enter_long",
        ] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["sell"] = 0

        return dataframe
