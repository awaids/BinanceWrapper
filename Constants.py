from binance.client import Client

CURRENCIES = [
    "BUSD",
    "AUD",
    "BRL",
    "EUR",
    "GBP",
    "RUB",
    "TRY",
    "TUSD",
    "USDC",
    "PAX",
    "BIDR",
    "DAI",
    "IDRT",
    "UAH",
    "NGN",
    "VAI",
    "BVND",
    "USDS",
    "USDSB",
    "SUSD",
    "USDP",
]

# Normally these klines are always empty
IGNORE_ASSETS = [
    "VEN",
    "ERD",
    "NPXS",
    "STROM",
    "BKRW",
    "LEND",
    "XZC",
    "STRAT",
    "MCO",
    "HC",
]

MIN_1 = Client.KLINE_INTERVAL_1MINUTE
MIN_5 = Client.KLINE_INTERVAL_5MINUTE
MIN_15 = Client.KLINE_INTERVAL_15MINUTE
MIN_30 = Client.KLINE_INTERVAL_30MINUTE
HOUR_1 = Client.KLINE_INTERVAL_1HOUR
DAY_1 = Client.KLINE_INTERVAL_1DAY

FIFTEEN_MIN_AGO = "15m ago UTC"
THIRTY_MIN_AGO = "30m ago UTC"
FIVE_MIN_AGO = "5m ago UTC"
ONE_WEEK_AGO = "7 day ago UTC"

# Epoch time constants
EPOCH_TIME_DIGITS = 10
SERVER_TO_EPOCH_TIME_DIVISOR = 1000

USDT = "USDT"
