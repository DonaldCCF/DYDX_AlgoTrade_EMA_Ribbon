from f_connection import connect_dydx
from f_messaging import send_message
from f_private import get_holding_position
from f_private import open_position, close_position
from f_signal import calculate_bull_bear
from constants import MARKET

# MAIN FUNCTION
if __name__ == "__main__":

    # Message on start
    send_message("EMA Ribbon Strategy Running...")

    # Connect to client
    try:
        print("Connecting to Client...")
        client = connect_dydx()
    except Exception as e:
        print("Error connecting to client: ", e)
        send_message(f"Failed to connect to client {e}")
        exit(1)

    holding_position = get_holding_position(client, MARKET)
    print("holding_position:", holding_position)

    bull_or_bear = calculate_bull_bear(client, holding_position)

    # Place trades for opening positions
    if holding_position != 0:
        if bull_or_bear == -1:
            print('[Strategy Signal] Short signal, Close the long position.')
            send_message('[Strategy Signal] Short signal, Close the long position.')
            close_position(client, 'SELL')
        if bull_or_bear == 1:
            print('[Strategy Signal] Long signal, Close the short position.')
            send_message('[Strategy Signal] Long signal, Close the short position.')
            close_position(client, 'BUY')
        if bull_or_bear == 0:
            print('[Strategy Signal] No exit signal, Continue waiting...')
            send_message('[Strategy Signal] No exit signal, Continue waiting...')

    # Manage trades for opening positions
    if holding_position == 0:
        if bull_or_bear == 1:
            print('[Strategy Signal] Long signal, Create a buy order...')
            send_message('[Strategy Signal] Long signal, Create a buy order...')
            open_position(client, 'BUY')
        if bull_or_bear == -1:
            print('[Strategy Signal] Short signal, Create a sell order...')
            send_message('[Strategy Signal] Short signal, Create a sell order...')
            open_position(client, 'SELL')
        if bull_or_bear == 0:
            print('[Strategy Signal] No entry signal, Continue waiting...')
            send_message('[Strategy Signal] No entry signal, Continue waiting...')
