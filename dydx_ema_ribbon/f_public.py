from f_utils import get_ISO_times, convert_time
from datetime import timedelta
import pandas as pd
import numpy as np
import time
from pprint import pprint


# Get Candles recent
def get_candles_recent(client, market, resolution):
    # Define output
    df = []

    # Protect API
    time.sleep(0.2)

    # Get data
    candles = client.public.get_candles(
        market=market,
        resolution=resolution,
        limit=100
    )
    # Structure data
    for candle in candles.data["candles"]:
        df.append({"datetime": candle["startedAt"], "open": candle["open"], "high": candle["high"],
                   "low": candle["low"], "close": candle["close"]})

    # Construct and return DataFrame

    df.reverse()
    df = pd.DataFrame(df)
    df.index = df["datetime"]
    del df["datetime"]
    pprint(df)
    return df


# Get Candles Historical
def get_candles_historical(client, market, resolution, entry_time):
    # Get relevant time periods for ISO from and to
    ISO_TIMES = get_ISO_times(entry_time, resolution)

    # Define output
    df = []

    # Extract historical price data for each timeframe
    for timeframe in ISO_TIMES.keys():

        # Confirm times needed
        tf_obj = ISO_TIMES[timeframe]
        from_iso = tf_obj["from_iso"]
        to_iso = tf_obj["to_iso"]
        # Protect rate limits
        time.sleep(0.2)

        # Get data
        candles = client.public.get_candles(
            market=market,
            resolution=resolution,
            from_iso=from_iso,
            to_iso=to_iso,
            limit=100
        )

        # Structure data
        for candle in candles.data["candles"]:
            df.append({"datetime": candle["startedAt"], "open": candle["open"], "high": candle["high"],
                       "low": candle["low"], "close": candle["close"],
                       "Token_vol": candle["baseTokenVolume"], "USD_vol": candle['usdVolume']})

    # Construct and return DataFrame
    df.reverse()
    df = pd.DataFrame(df)
    df["datetime"] = pd.to_datetime(df["datetime"])
    # df["datetime"] = (pd.to_datetime(df["datetime"]) + timedelta(seconds=28800)).dt.strftime("%d-%m-%Y %H:%M:%S")
    df.index = df["datetime"]
    del df["datetime"]
    return df.astype(float)