from f_private import place_market_order, check_order_status
from datetime import datetime
import time


# Class: Agent for managing opening and checking trades
class BotAgent:

    """
    Primary function of BotAgent handles opening and checking order status
    """

    # Initialize class
    def __init__(
            self,
            client,
            market,
            side,
            size,
            price,
            accept_failsafe_price,
    ):

        # Initialize class variables
        self.client = client
        self.market = market
        self.side = side
        self.size = size
        self.price = price
        self.accept_failsafe_price = accept_failsafe_price

        # Initialize output variable
        # Pair status options are FAILED, LIVE, CLOSE, ERROR
        self.order_dict = {
            "market": market,
            "order_id": "",
            "order_size": size,
            "order_side": side,
            "order_time": "",
            "order_status": "",
            "comments": "",
        }

    # Check order status by id
    def check_order_status_by_id(self, order_id):

        # Allow time to process
        time.sleep(2)

        # Check order status
        order_status = check_order_status(self.client, order_id)

        # Guard: If order cancelled move onto next Pair
        if order_status == "CANCELED":
            print(f"{self.market} - Order cancelled...")
            self.order_dict["order_status"] = "FAILED"
            return "failed"

        # Guard: If order not filled wait until order expiration
        if order_status != "FAILED":
            time.sleep(15)
            order_status = check_order_status(self.client, order_id)

            # Guard: If order cancelled move onto next Pair
            if order_status == "CANCELED":
                print(f"{self.market} - Order cancelled...")
                self.order_dict["order_status"] = "FAILED"
                return "failed"

            # Guard: If not filled, cancel order
            if order_status != "FILLED":
                self.client.private.cancel_order(order_id=order_id)
                self.order_dict["order_status"] = "ERROR"
                print(f"{self.market} - Order error...")
                return "error"

        # Return live
        return "live"

        # Open trades

    def open_trades(self):

        # Print status
        print("---------------------------------------------------------")
        print(f"{self.market}: Placing order...")
        print(f"Side: {self.side}, Size: {self.size}, Price: {self.price}")
        print("---------------------------------------------------------")

        # Place Base Order
        try:
            order = place_market_order(
                self.client,
                market=self.market,
                side=self.side,
                size=self.size,
                price=self.price,
                reduce_only=False
            )

            # Store the order id
            self.order_dict["order_id"] = order["order"]["id"]
            self.order_dict["order_time"] = datetime.now().isoformat()
        except Exception as e:
            self.order_dict["order_status"] = "ERROR"
            self.order_dict["comments"] = f"Market  {self.market}: , {e}"
            return self.order_dict

        # Ensure order is live before processing
        order_status = self.check_order_status_by_id(self.order_dict["order_id"])

        # Guard: Aborder if order failed
        if order_status != "live":
            self.order_dict["order_status"] = "ERROR"
            self.order_dict["comments"] = f"{self.market} failed to fill"
            return self.order_dict

        # Return success result
        else:
            self.order_dict["order_status"] = "LIVE"
            return self.order_dict