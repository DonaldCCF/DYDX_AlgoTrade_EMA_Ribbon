import time
from constants import RESOLUTION, MARKET, WINDOW1, WINDOW2, WINDOW3, WINDOW4, STOP_LOSS, ATR_MULTIPLIER
from f_utils import format_number, convert_time
from f_public import get_candles_recent, get_candles_historical
from f_messaging import send_message
import pandas_ta as ta
import pandas as pd


def calculate_bull_bear(client, position):
    signal = 0

    if position == 0:
        data = get_candles_recent(client, MARKET, RESOLUTION)
        data.index = pd.to_datetime(data.index)

        data = get_candles_recent(client, MARKET, RESOLUTION)
        data.index = pd.to_datetime(data.index)

        # Calculate EMA
        e1 = ta.ema(data['close'], length=WINDOW1)
        e2 = ta.ema(data['close'], length=WINDOW2)
        e3 = ta.ema(data['close'], length=WINDOW3)
        e4 = ta.ema(data['close'], length=WINDOW4)
        last_price = data['close'][-1]

        if (e1[-1] > e2[-1]) and (e2[-1] > e3[-1]) \
                and (e3[-1] > e4[-1]) and (last_price > e1[-1]):
            signal = 1

        if (e1[-1] < e2[-1]) and (e2[-1] < e3[-1]) \
                and (e3[-1] < e4[-1]) and (last_price < e1[-1]):
            signal = -1

        return signal

    if position != 0:
        exchange_pos = client.private.get_positions(status="OPEN")
        all_exc_pos = pd.DataFrame(exchange_pos.data["positions"])

        entry_price = all_exc_pos["entryPrice"].loc[all_exc_pos.market == MARKET].astype(str).astype(float)
        entry_time = convert_time(pd.to_datetime(all_exc_pos["createdAt"][0]))
        data = get_candles_historical(client, MARKET, RESOLUTION, entry_time).astype(float)
        last_price = data['close'][-1]
        atr = ta.atr(data['high'], data['low'], data['close'])
        
        if position == 1:
            send_message(f"Current Position: Long, {entry_price[0]}")
            if (entry_price[0] - last_price) / entry_price[0] > STOP_LOSS:
                signal = -1

            enti = pd.to_datetime(all_exc_pos["createdAt"][0])
            max_pnl = data['close'].loc[(data.index > enti) & (data.index < data.index[-1])]
            if (max_pnl.max() - last_price >= ATR_MULTIPLIER * atr[-1]) and \
                    (max_pnl.max() - entry_price[0] >= ATR_MULTIPLIER * atr[-1]):
                signal = -1

        else:
            send_message(f"Current Position: Short, {entry_price[0]}")
            if (last_price - entry_price[0]) / entry_price[0] > STOP_LOSS:
                signal = 1

            enti = pd.to_datetime(all_exc_pos["createdAt"][0])
            max_pnl = data['close'].loc[(data.index > enti) & (data.index < data.index[-1])]
            if (last_price - max_pnl.min() >= ATR_MULTIPLIER * atr[-1]) and \
                    (entry_price[0] - max_pnl.min() >= ATR_MULTIPLIER * atr[-1]):
                signal = 1

        return signal
