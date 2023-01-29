from f_utils import format_number, convert_time
from f_public import get_candles_historical
from f_private import place_market_order, is_open_positions
from f_messaging import send_message
from constants import MARKET, RESOLUTION, STOP_LOSS, ATR_MULTIPLIER
import pandas_ta as ta
from datetime import timedelta
from f_bot_agent import BotAgent
import pandas as pd
import json
import time


def exit_signal(client, pos):

    # Get all open positions per trading platform
    exchange_pos = client.private.get_positions(status="OPEN")
    all_exc_pos = pd.DataFrame(exchange_pos.data["positions"])

    signal = ""

    entry_price = all_exc_pos["entryPrice"].loc[all_exc_pos.market == MARKET].astype(str).astype(float)
    entry_time = convert_time(pd.to_datetime(all_exc_pos["createdAt"][0]))
    data = get_candles_historical(client, MARKET, RESOLUTION, entry_time).astype(float)
    last_price = data['close'][-1]
    atr = ta.atr(data['high'], data['low'], data['close'])

    if pos == 1:
        # Stop loss
        if (entry_price[0] - last_price) / entry_price[0] -1 > STOP_LOSS:
            signal = "SELL"

        # ATR offset detection
        enti = pd.to_datetime(all_exc_pos["createdAt"][0])
        max_pnl = data['close'].loc[(data.index > enti) & (data.index < data.index[-1])]

        if (max_pnl.max() - last_price >= ATR_MULTIPLIER * atr[-1]) and \
                (max_pnl.max() - entry_price[0] >= ATR_MULTIPLIER * atr[-1]):
            signal = "SELL"

    if pos == -1:
        if (last_price - entry_price[0]) / entry_price[0] -1 > STOP_LOSS:
            signal = "BUY"

        enti = pd.to_datetime(all_exc_pos["createdAt"][0])
        max_pnl = data['close'].loc[(data.index > enti) & (data.index < data.index[-1])]
        if (last_price - max_pnl.min() >= ATR_MULTIPLIER * atr[-1]) and \
                (entry_price[0] - max_pnl.min() >= ATR_MULTIPLIER * atr[-1]):
            signal = "BUY"

    return signal, last_price



# Manage trade exits
def manage_trade_exits(client, pos):
    """
    Manage exiting open positions
    Based upon criteria set in constants
  """

    # Initialize saving output
    save_output = []

    # Opening JSON file
    try:
        open_positions_file = open("bot_agents.json")
        open_positions_dict = json.load(open_positions_file)
    except:
        return "complete"

    # Guard: Exit if no open positions in file
    if len(open_positions_dict) < 1:
        return "complete"

    # Exit trade according to any exit trade rules
    markets = client.public.get_markets().data
    is_open = is_open_positions(client, MARKET)

    # Close positions if triggered
    if is_open:
        exchange_pos = client.private.get_positions(status="OPEN")
        all_exc_pos = pd.DataFrame(exchange_pos.data["positions"])
        entry_price = all_exc_pos["entryPrice"].loc[all_exc_pos.market == MARKET].astype(str).astype(float)
        side = all_exc_pos["side"][0]
        size = all_exc_pos["size"].astype(float)[0]

        side, price = exit_signal(client, pos)
        if side == "":
            print("No exit signal...")
            send_message(f"No exit signal... Last Price: {price}. Side: {side}, Price: {entry_price}, Size: {size}")
            return

        accept_price = price * 1.05 if side == "BUY" else price * 0.95
        tick_size = markets["markets"][MARKET]["tickSize"]
        accept_price = format_number(accept_price, tick_size)

        # Close positions
        try:

            # Close position for market 1
            print(">>> Closing position <<<")
            print(f"Closing position for {MARKET}")

            close_order = place_market_order(
                client,
                market=MARKET,
                side=side,
                size=size,
                price=accept_price,
                reduce_only=True,
            )

            print(close_order["order"]["id"])
            print(">>> Closing <<<")

            # Protect API
            time.sleep(1)

            send_message(f"Exit signal detected! Closing position... "
                         f"Last Price: {price}. Side: {side}, Price: {entry_price}, Size: {size}")

        except Exception as e:
            print(f"Exit failed for {MARKET}")
            save_output.append(MARKET)

        # Keep record if items and save
        else:
            save_output.append(MARKET)

    # Save remaining items
    print("Saving file...")
    with open("bot_agents.json", "w") as f:
        json.dump(save_output, f)
