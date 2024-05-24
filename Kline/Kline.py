import pandas as pd
from datetime import datetime
from typing import List, Any
from BinanceWrapper.Constants import SERVER_TO_EPOCH_TIME_DIVISOR


def timestr(timestamp) -> str:
    """Convert timestamp to human-readabke time"""
    return datetime.fromtimestamp(int(timestamp / SERVER_TO_EPOCH_TIME_DIVISOR))


class KlinesDataframe:
    """This class will wrap the klines provided by the binance into a Dataframe"""

    columns = [
        "OpenTime",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "CloseTime",
        "QuoteAssetVol",
        "NumberTrades",
        "BuyBaseAssetVol",
        "BuyQuoteAssetVol",
        "Ignore",
    ]

    def __init__(self, klines: List[List[Any]]) -> None:
        self._df = pd.DataFrame(klines, columns=self.columns, dtype=float)
        self._df["OpenTime"] = self.df["OpenTime"].map(timestr)
        self._df["CloseTime"] = self.df["CloseTime"].map(timestr)

    @property
    def df(self) -> pd.DataFrame:
        return self._df

    @property
    def n_rows(self) -> pd.DataFrame:
        return self._df.shape[0]
