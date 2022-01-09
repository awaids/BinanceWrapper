from ..Constants import SERVER_TO_EPOCH_TIME_DIVISOR
from ..Utils import get_time_str as utils_get_time_str
'''
{
    "priceChange": "-94.99999800",
    "priceChangePercent": "-95.960",
    "weightedAvgPrice": "0.29628482",
    "prevClosePrice": "0.10002000",
    "lastPrice": "4.00000200",
    "bidPrice": "4.00000000",
    "askPrice": "4.00000200",
    "openPrice": "99.00000000",
    "highPrice": "100.00000000",
    "lowPrice": "0.10000000",
    "volume": "8913.30000000",
    "openTime": 1499783499040,
    "closeTime": 1499869899040,
    "fristId": 28385,   # First tradeId
    "lastId": 28460,    # Last tradeId
    "count": 76         # Trade count
}
'''

class Ticker:
    # https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client.get_ticker
    def __init__(self, Tick: dict):
        self.symbol = Tick['symbol']
        self.priceChange = float(Tick['priceChange'])
        self.priceChangePercent = float(Tick['priceChangePercent'])
        self.openPrice = float(Tick['openPrice'])
        self.highPrice = float(Tick['highPrice'])
        self.lowPrice = float(Tick['lowPrice'])
        self.weightedAvgPrice = float(Tick['weightedAvgPrice'])
        self.volume = float(Tick['volume'])
        self.openTime = float(Tick['openTime']) / SERVER_TO_EPOCH_TIME_DIVISOR
        self.closeTime = float(Tick['closeTime']) / SERVER_TO_EPOCH_TIME_DIVISOR

    def get_symbol(self) -> str:
        return self.symbol

    def get_volume(self) -> float:
        return self.volume

    def get_priceChange(self) -> float:
        return self.priceChange

    def get_weightedAvgPrice(self) -> float:
        return self.weightedAvgPrice

    def __str__(self):
        return f'Tick({self.symbol}/{self.weightedAvgPrice}): Change%({self.priceChangePercent}) HighPrice({self.highPrice}) Avg({self.weightedAvgPrice}) LowPrice({self.lowPrice}) closeTime({utils_get_time_str(self.closeTime)})'
