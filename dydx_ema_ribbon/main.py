from dydx_tbpy.f_connection import connect_dydx
from dydx_tbpy.f_messaging import send_message
from dydx_tbpy.f_private import abort_all_positions, get_holding_position
from f_entry import open_positions
from f_exit import manage_trade_exits
from constants import ABORT_ALL_POSITIONS, MANAGE_EXITS, PLACE_TRADES, MARKET

# MAIN FUNCTION
if __name__ == "__main__":

    # Message on start
    send_message("Bot launch successful")

    # Connect to client
    try:
        print("Connecting to Client...")
        client = connect_dydx()
    except Exception as e:
        print("Error connecting to client: ", e)
        send_message(f"Failed to connect to client {e}")
        exit(1)

    if ABORT_ALL_POSITIONS:
        try:
            print("Closing all positions...")
            close_orders = abort_all_positions(client)
        except Exception as e:
            print("Error closing all positions: ", e)
            send_message(f"Error closing all positions {e}")
            exit(1)

    # # Run as always on
    # while True:

    position = get_holding_position(client, MARKET)

    # Manage trades for opening positions
    if position != 0:
        try:
            print("Managing exits...")
            manage_trade_exits(client, position)
        except Exception as e:
            print("Error managing exiting positions: ", e)
            send_message(f"Error managing exiting positions {e}")
            exit(1)

    # Place trades for opening positions
    if position == 0:
        try:
            print("Detecting trading signal...")
            open_positions(client)
        except Exception as e:
            print("Error opening trades: ", e)
            send_message(f"Error opening trades {e}")
            exit(1)
