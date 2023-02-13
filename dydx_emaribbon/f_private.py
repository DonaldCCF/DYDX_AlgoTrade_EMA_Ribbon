from datetime import datetime, timedelta
from f_messaging import send_message
from f_public import get_current_price
import pandas as pd
import time
from constants import USD_PER_TRADE, USD_MIN_COLLATERAL, MARKET
from f_utils import format_number


# Get existing open positions
def is_open_positions(client, market):
    # Protect API
    time.sleep(0.2)

    # Get positions
    all_positions = client.private.get_positions(
        market=market,
        status="OPEN"
    )

    # Determine if open
    if len(all_positions.data["positions"]) > 0:
        return True
    else:
        return False


def get_holding_position(client, market):
    position = 0
    exchange_pos = client.private.get_positions(status="OPEN", market=market)
    all_exc_pos = pd.DataFrame(exchange_pos.data["positions"])
    if len(all_exc_pos) > 0:
        side = all_exc_pos["side"][0]
        if side == "LONG":
            position = 1
        if side == "SHORT":
            position = -1
    return position


# Place market order
def place_market_order(client, market, side, size, price, reduce_only):
    # Get Position id
    account_response = client.private.get_account()
    position_id = account_response.data["account"]["positionId"]

    # Get expiration time
    server_time = client.public.get_time()
    expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(seconds=28870)

    # Place an order
    placed_order = client.private.create_order(
        position_id=position_id,  # required for creating the order signature
        market=market,
        side=side,
        order_type="MARKET",
        post_only=False,
        size=size,
        price=price,
        limit_fee='0.015',
        expiration_epoch_seconds=expiration.timestamp(),
        time_in_force="FOK",
        reduce_only=reduce_only
    )

    print(placed_order.data)
    send_message(placed_order.data)

    # Return result
    return placed_order.data


def open_position(client, side):
    # Get markets from referencing of min order size, tick size etc
    markets = client.public.get_markets().data
    time.sleep(3)
    price = get_current_price(client)

    # Get acceptable price in string format with correct number of decimals
    accept_price = float(price) * 1.1 if side == "BUY" else float(price) * 0.9
    failsafe_price = float(price) * 1.7 if side == "BUY" else float(price) * 0.5
    tick_size = markets["markets"][MARKET]["tickSize"]

    # Format prices
    accept_price = format_number(accept_price, tick_size)
        
    # Get size
    account = client.private.get_account()
    
    # USD_PER_TRADE = float(account.data["account"]["equity"]) * EQUITY_USED
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
        free_collateral = float(account.data["account"]["freeCollateral"])
        print(f"Balance: {free_collateral} and minimum at {USD_MIN_COLLATERAL}")

        # Guard: Ensure collateral
        if free_collateral < USD_MIN_COLLATERAL:
            exit(1)

        # Open position
        print(">>> Opening position <<<")
        print(f"Opening position for {MARKET}")

        try:
            open_order = place_market_order(
                client,
                market=MARKET,
                side=side,
                size=size,
                price=accept_price,
                reduce_only=False
            )
        except Exception as e:
            print(e)

        # Protect API
        time.sleep(1)


def close_position(client, side):

    # Exit trade according to any exit trade rules
    markets = client.public.get_markets().data
    is_open = is_open_positions(client, MARKET)

    time.sleep(3)
    price = get_current_price(client)

    # Close positions if triggered
    if is_open:
        exchange_pos = client.private.get_positions(status="OPEN")
        all_exc_pos = pd.DataFrame(exchange_pos.data["positions"])
        
        quantity = abs(all_exc_pos["size"].astype(float)[0])
        step_size = markets["markets"][MARKET]["stepSize"]
        size = format_number(quantity, step_size)

        accept_price = price * 1.1 if side == "BUY" else price * 0.9
        tick_size = markets["markets"][MARKET]["tickSize"]
        accept_price = format_number(accept_price, tick_size)

        # Close position
        print(">>> Closing position <<<")
        print(f"Closing position for {MARKET}")

        try:
            close_order = place_market_order(
                client,
                market=MARKET,
                side=side,
                size=size,
                price=accept_price,
                reduce_only=True,
            )
        except Exception as e:
            print(e)

        # Protect API
        time.sleep(1)
