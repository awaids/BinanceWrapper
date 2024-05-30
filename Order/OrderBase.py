from __future__ import annotations
from abc import ABC
from ..BinanceManager import MyBinanceManager
from ..BinanceManager import Symbol

# Constants
_local_bm = MyBinanceManager("OrderBase")


class OrderBase(ABC):
    def __init__(self, orderDict: dict):
        self._d = orderDict

    def update(self) -> OrderBase:
        """Updates the current instance of the order"""
        self._d = _local_bm.get_order(symbolName=self.symbolName, orderId=self.orderId)
        return self

    # FIXED dict values
    @property
    def orderId(self) -> str:
        return self._d.get("orderId")

    @property
    def symbolName(self) -> str:
        return self._d.get("symbol")

    @property
    def price(self) -> float:
        return float(self._d.get("price"))

    @property
    def origQty(self) -> float:
        return float(self._d.get("origQty"))

    @property
    def executedQty(self) -> float:
        return float(self._d.get("executedQty"))

    @property
    def status(self) -> str:
        return self._d.get("status")

    @property
    def side(self) -> str:
        return self._d.get("side")

    @property
    def type(self) -> str:
        return self._d.get("type")

    @property
    def updateTime(self) -> float:
        return float(self._d.get("updateTime"))

    # Basic Properties
    @property
    def latestStatus(self):
        """Updates and get latest status
        Note: updates the OrderBase"""
        return self.update().status

    @property
    def isAlive(self):
        """Returns True if the order is still live!
        Note: updates the OrderBase"""
        return (
            False
            if self.latestStatus in ["CANCELED", "FILLED", "REJECTED", "EXPIRED"]
            else True
        )

    @property
    def investedCash(self) -> float:
        """Returns the amount invested in the order"""
        return self.price * self.executedQty

    # Binance based properties
    @property
    def symbolInfo(self) -> Symbol:
        return _local_bm.get_symbol_info(symbolName=self.symbolName)

    def get_ticker_price(self) -> float:
        return _local_bm.getSymbolTickerPrice(symbolName=self.symbolName)

    # Functions to overload
    def telegramMsg(self) -> str:
        """Constructs a telegram message"""
        # https://stackoverflow.com/a/61225235
        return f"{self.type}-{self.side}: {self.symbolName}\nPrice: {self.price}\norigQty: {self.origQty}\nStatus({self.status})".replace(
            "_", "-"
        )

    def __str__(self):
        return f"orderId({self.orderId}) {self.symbolName} {self.type}-{self.side} Status({self.status}) Price({self.price}) origQty({self.origQty}) executedQty({self.executedQty})"

    # Parsing and Synthesizing helping functions
    @property
    def synth(self) -> dict:
        return self._d
