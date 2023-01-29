from constants import USD_PER_TRADE, USD_MIN_COLLATERAL, \
    RESOLUTION, MARKET, WINDOW1, WINDOW2, WINDOW3, WINDOW4
from f_utils import format_number,convert_time
from f_public import get_candles_recent
from f_private import is_open_positions
from f_bot_agent import BotAgent
from f_messaging import send_message
import pandas_ta as ta
import pandas as pd
import json


# Detect EMA Ribbon signal
def entry_signal(client):
    # Get K Line
    data = get_candles_recent(client, MARKET, RESOLUTION)
    data.index = pd.to_datetime(data.index)

    # Calculate EMA
    e1 = ta.ema(data['close'], length=WINDOW1)
    e2 = ta.ema(data['close'], length=WINDOW2)
    e3 = ta.ema(data['close'], length=WINDOW3)
    e4 = ta.ema(data['close'], length=WINDOW4)
    price = data['close'].astype(float)[-1]
    # Judge long or short
    signal = ""
    if (e1[-1] > e2[-1]) and (e2[-1] > e3[-1]) \
            and (e3[-1] > e4[-1]) and (price > e1[-1]):
        print("ok1")
        signal = "BUY"

    if (e1[-1] < e2[-1]) and (e2[-1] < e3[-1]) \
            and (e3[-1] < e4[-1]) and (price < e1[-1]):
        print("ok2")
        signal = "SELL"

    return signal, price


# Open positions
def open_positions(client):
    """
    Manage finding triggers for trade entry
    Store trades for managing later on on exit function
    """

    # Get markets from referencing of min order size, tick size etc

    markets = client.public.get_markets().data

    # Initialize container for BotAgent results
    bot_agents = []

    is_open = is_open_positions(client, MARKET)

    if not is_open:

        side, price = entry_signal(client)
        if side == "":
            print("No entry signal...")
            send_message("No entry signal...")
            return
        # Get acceptable price in string format with correct number of decimals
        accept_price = float(price) * 1.01 if side == "BUY" else float(price) * 0.99
        failsafe_price = float(price) * 1.7 if side == "BUY" else float(price) * 0.5
        tick_size = markets["markets"][MARKET]["tickSize"]

        # Format prices
        accept_price = format_number(accept_price, tick_size)

        # Get size
        quantity = USD_PER_TRADE / price
        step_size = markets["markets"][MARKET]["stepSize"]

        # Format sizes
        size = format_number(quantity, step_size)

        # Ensure size
        min_order_size = markets["markets"][MARKET]["minOrderSize"]
        check = float(quantity) > float(min_order_size)

        # If checks pass, place trades
        if check:
            # Check account balance
            account = client.private.get_account()
            free_collateral = float(account.data["account"]["freeCollateral"])
            print(f"Balance: {free_collateral} and minimum at {USD_MIN_COLLATERAL}")

            # Guard: Ensure collateral
            if free_collateral < USD_MIN_COLLATERAL:
                exit(1)

            # Create Bot Agent
            bot_agent = BotAgent(
                client,
                market=MARKET,
                side=side,
                size=size,
                price=accept_price,
                accept_failsafe_price=failsafe_price,
            )

            # Open Trades
            bot_open_dict = bot_agent.open_trades()
            # Handle success in opening trades
            if bot_open_dict["order_status"] == "LIVE":
                # Append to list of bot agents
                bot_agents.append(bot_open_dict)
                del bot_open_dict

                # Confirm live status in print
                print("Trade status: Live")
                print("---")

            exchange_pos = client.private.get_positions(status="OPEN")
            all_exc_pos = pd.DataFrame(exchange_pos.data["positions"])

            if len(all_exc_pos) > 0:
                entry_price = all_exc_pos["entryPrice"].loc[all_exc_pos.market == MARKET].astype(str).astype(float)
                entry_time = convert_time(pd.to_datetime(all_exc_pos["createdAt"][0]))
                side = all_exc_pos["side"][0]
                size = all_exc_pos["size"].astype(float)[0]
                send_message(f"Open {side}! Entry Time: {entry_time}, Price: {entry_price}, Size: {size}")

    # Save agents
    print(f"Success: Manage open trades checked")
    if len(bot_agents) > 0:
        with open("bot_agents.json", "w") as f:
            json.dump(bot_agents, f)
