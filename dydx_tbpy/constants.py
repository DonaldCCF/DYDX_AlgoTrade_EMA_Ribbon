from dydx3.constants import API_HOST_GOERLI, API_HOST_MAINNET
from decouple import config

# MODE = "PRODUCTION"
MODE = "DEVELOPMENT"

# Close all open positions and orders
ABORT_ALL_POSITIONS = True

# Find Cointegrated Pairs
FIND_COINTEGRATED = False

# Manage Exits
MANAGE_EXITS = True

# Place Trades
PLACE_TRADES = True

# Resolution
RESOLUTION = "1HOUR"

# Stats Window
WINDOW = 21

# Thresholds - Opening
MAX_HALF_LIFE = 24
ZSCORE_THRESH = 1.5
USD_PER_TRADE = 50
USD_MIN_COLLATERAL = 1880

# Thresholds - Closing
CLOSE_AT_ZSCORE_CROSS = True

# Ethereum Address
ETHEREUM_ADDRESS = '0xb0F51EaC224235323c75a8B086F65362A0052C06'

# KEYS - PRODUCTION
# Must be on Mainnet in DYDX
STARK_PRIVATE_KEY_MAINNET = config("STARK_PRIVATE_KEY_MAINNET")
DYDX_API_KEY_MAINNET = config("DYDX_API_KEY_MAINNET")
DYDX_API_SECRET_MAINNET = config("DYDX_API_SECRET_MAINNET")
DYDX_API_PASSPHRASE_MAINNET = config("DYDX_API_PASSPHRASE_MAINNET")

# KEYS - DEVELOPMENT
# Must be on Testnet in DYDX
STARK_PRIVATE_KEY_TESTNET = config("STARK_PRIVATE_KEY_TESTNET")
DYDX_API_KEY_TESTNET = config("DYDX_API_KEY_TESTNET")
DYDX_API_SECRET_TESTNET =config("DYDX_API_SECRET_TESTNET")
DYDX_API_PASSPHRASE_TESTNET = config("DYDX_API_PASSPHRASE_TESTNET")

# KEYS - Export
STARK_PRIVATE_KEY = STARK_PRIVATE_KEY_MAINNET if MODE == "PRODUCTION" \
    else STARK_PRIVATE_KEY_TESTNET
DYDX_API_KEY = DYDX_API_KEY_MAINNET if MODE == "PRODUCTION" \
    else DYDX_API_KEY_TESTNET
DYDX_API_SECRET = DYDX_API_SECRET_MAINNET if MODE == "PRODUCTION" \
    else DYDX_API_SECRET_TESTNET
DYDX_API_PASSPHRASE = DYDX_API_PASSPHRASE_MAINNET if MODE == "PRODUCTION" \
    else DYDX_API_PASSPHRASE_TESTNET

# HOST - Export
HOST = API_HOST_MAINNET if MODE == "PRODUCTION" else API_HOST_GOERLI

# HTTP PROVIDER
HTTP_PROVIDER_MAINNET = "https://eth-mainnet.g.alchemy.com/v2/BUh4q-9VY8I-7vaYvRRq1MHI20efuHQW"
HTTP_PROVIDER_TESTNET = "https://eth-goerli.g.alchemy.com/v2/BreFktEgNA_M39-WdPamkTRJz-hFFjA9"
HTTP_PROVIDER = HTTP_PROVIDER_MAINNET if MODE == "PRODUCTION" else HTTP_PROVIDER_TESTNET