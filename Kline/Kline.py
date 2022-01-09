import pandas as pd
from ..Constants import SERVER_TO_EPOCH_TIME_DIVISOR

def timestr(timestamp) -> str:
    from datetime import datetime
    return datetime.fromtimestamp(int(timestamp/SERVER_TO_EPOCH_TIME_DIVISOR))


class KlinesDataframe:
    columns = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime',
               'QuoteAssetVol', 'NumberTrades', 'BuyBaseAssetVol', 'BuyQuoteAssetVol', 'Ignore']

    def __init__(self, klines: list):
        # TODO: Drop the last row, at this is the current Kline working!
        self.df = pd.DataFrame(klines, columns=self.columns, dtype=float)
        self.df['OpenTime'] = self.df['OpenTime'].map(timestr)
        self.df['CloseTime'] = self.df['CloseTime'].map(timestr)