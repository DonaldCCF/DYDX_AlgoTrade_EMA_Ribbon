import time
from datetime import datetime, timedelta
import pandas as pd
from dydx_tbpy.f_connection import connect_dydx
from pprint import pprint
from constants import MARKET, RESOLUTION
from dydx_tbpy.f_public import get_candles_historical
from dydx_tbpy.f_utils import get_ISO_times, convert_time, format_time
from f_bot_agent import BotAgent
import math
pd.set_option('display.max_columns', 500)

try:
    print("Connecting to Client...")
    client = connect_dydx()
except Exception as e:
    print("Error connecting to client: ", e)
    exit(1)

# account_response = client.private.get_account()
# position_id = account_response.data["account"]["positionId"]
#
server_time = client.public.get_time()
print(server_time.data["iso"])
# expiration = datetime.fromisoformat(server_time.data["iso"].replace("Z", "")) + timedelta(seconds=28870)
#
exchange_pos = client.private.get_positions(status="OPEN", market="BTC-USD")
all_exc_pos = pd.DataFrame(exchange_pos.data["positions"]).astype(str)
# if len(all_exc_pos) == 0:
#     print('explosion!')
# print(all_exc_pos)
# entry = all_exc_pos["entryPrice"].astype(float)[0]
# side = all_exc_pos["side"][0]
# size = all_exc_pos["size"].astype(float)[0]
# print()

# entry_time = convert_time(pd.to_datetime(all_exc_pos["createdAt"][0]))
# candle = get_candles_historical(client, MARKET, RESOLUTION, entry_time)
# pprint(candle)

entry = all_exc_pos["entryPrice"].loc[all_exc_pos.market == MARKET].astype(str).astype(float)
entry_time = convert_time(pd.to_datetime(all_exc_pos["createdAt"][0]))
data = get_candles_historical(client, MARKET, RESOLUTION, entry_time)
price = data['close'].astype(float)[-1]
max_profit = data['close'].loc[(data.index > pd.to_datetime(all_exc_pos["createdAt"][0])) & (data.index < data.index[-1])].astype(float)
print(max_profit.max())