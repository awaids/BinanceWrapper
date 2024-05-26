from .AsynClient.BaseAsyncClient import RUC, MY_ASYNC_CLIENT
from python_log_indenter import IndentedLoggerAdapter
from . import Constants
import time
from . import Utils as utl
from .Kline.Kline import KlinesDataframe
from .Ticker.Ticker import Ticker
from .Symbol.Symbol import Symbol
from typing import List, Dict


def BIN_RETRY(func):
    # New decorator for all the binance methods
    def result(*args, **kwargs):
        retries = 5
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Exception Thrown: {e}")
                print(f"Retrying({retries - i}) .....")
                time.sleep(5 * i)
                pass
        raise e

    return result


# NOTE: Please keep the Binance releated functions here only!
class MyBinanceManager:
    def __init__(self, logger: IndentedLoggerAdapter = None) -> None:
        # Setup logger
        self.log = (
            utl.get_indentedLogger(loggername="MyBinanceManager")
            if logger is None
            else logger
        )

    @property
    def client(self):
        """Use the async client here"""
        return MY_ASYNC_CLIENT

    def get_exchange_info(self):
        return RUC(self.client.get_exchange_info())

    def get_account_snapshot(self, type: str):
        return RUC(self.client.get_account_snapshot(type=type))

    def getSpotAccountSnapshot(self):
        # https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client.get_account_snapshot
        return self.get_account_snapshot(type="SPOT")

    def get_server_time(self) -> float:
        """Return current server time"""
        return float((RUC(self.client.get_server_time())).get("serverTime"))

    def getServerLocalTimeOffset(self) -> float:
        """Difference betweeen given Local Time and current server time"""
        return (
            self.get_server_time() / Constants.SERVER_TO_EPOCH_TIME_DIVISOR
        ) - utl.get_local_time()

    def get_all_tickers(self) -> List[Dict[str, str]]:
        # Example of dict {"symbol": "LTCBTC", "price": "4.00000200"}
        return RUC(self.client.get_all_tickers())

    def get_account(self) -> Dict:
        # https://binance-docs.github.io/apidocs/spot/en/#account-information-user_data
        return RUC(self.client.get_account())

    def getAccountBalances(self) -> List[Dict]:
        return self.get_account().get("balances")

    @utl.cache
    def get_symbol_info(self, symbolName: str) -> Symbol:
        return Symbol(SymbolInfo=RUC(self.client.get_symbol_info(symbol=symbolName)))

    @BIN_RETRY
    def get_klines(
        self,
        symbolName: str,
        interval: str,
        limit: int,
    ) -> KlinesDataframe:
        return KlinesDataframe(
            RUC(
                self.client.get_klines(
                    symbol=symbolName,
                    interval=interval,
                    limit=limit,
                )
            )
        )

    @BIN_RETRY
    def get_historical_klines(
        self, symbolName: str, interval: str, startTime: str
    ) -> KlinesDataframe:
        return KlinesDataframe(
            RUC(
                self.client.get_historical_klines(
                    symbol=symbolName, interval=interval, start_str=startTime
                )
            )
        )

    def get_ticker(self, symbolName: str) -> Ticker:
        """Returns (priceChangePercent, weightedAvg) for last 24 hours"""
        return Ticker(RUC(self.client.get_ticker(symbol=symbolName)))

    @BIN_RETRY
    def getSymbolTickerPrice(self, symbolName: str) -> float:
        try:
            price = float(
                RUC(self.client.get_symbol_ticker(symbol=symbolName)).get("price")
            )
        except Exception as e:
            if "Invalid symbol." in e.message:
                return 0.0
        return price

    def get_asset_balance(self, asset: str):
        return RUC(self.client.get_asset_balance(asset=asset))

    def getFreeAsset(self, asset: str):
        return float(self.get_asset_balance(asset=asset).get("free"))

    def get_all_orders(self, symbolName: str) -> list:
        return RUC(self.client.get_all_orders(symbol=symbolName))

    def getMostRecentOrder(self, symbolName: str):
        return self.get_all_orders(symbolName=symbolName)[-1]

    def get_open_orders(self):
        for _ in range(5):
            try:
                return RUC(self.client.get_open_orders())
            except Exception as e:
                self.log.error(str(e))
                pass
        self.log.error(f"get_open_orders: failed!")
        exit(1)

    def getFiatDepositHistory(self):
        return RUC(
            self.client.get_fiat_deposit_withdraw_history(
                transactionType=0,  # 0 - deposits, 1 - withdrawn
                beginTime=1609459200,  # Begin time 01/02/2021
            )
        )

    def getAllOpenStopLossLimitOrders(self):
        stopLossOrders = list(
            filter(lambda x: x.get("type") == "STOP_LOSS_LIMIT", self.get_open_orders())
        )
        return stopLossOrders

    @BIN_RETRY
    def get_order(self, symbolName: str, orderId: int):
        return RUC(self.client.get_order(symbol=symbolName, orderId=orderId))

    def get_order_book(self, symbolName: str) -> Dict:
        return RUC(self.client.get_order_book(symbol=symbolName, limit=10000))

    def getMarketDepthRatio(self, symbolName: str, percentage: float = 10.0) -> float:
        """Returns the market depth ratio percentage i.e. (-26.3%) for the given symbol
        and percent(need to provided as 10.0 for 10%) for the ask/bid difference to price
        Positive MDR suggests that more people want to buy as opposed to sell and vice-versa.
        so Higher MDR coins should "Technically" see a price increment
        Each depth ask/bid looks like: [price, qty]
        NOTE: somehow the bid/ask qty cannot be replicated as the one shown in the depth graph
        Still dont know why its so, however, I have checked that the qty are okay with respect to the orderbook!
        """
        depth = self.get_order_book(symbolName=symbolName)
        asks = depth.get("asks")
        bids = depth.get("bids")
        if len(asks) == 0 or len(bids) == 0:
            raise Exception("Bid/Asks empty")

        # Compute price for given percentage
        asks_price = float(asks[0][0]) * (1 + percentage / 100)
        bids_price = float(bids[0][0]) * (1 - percentage / 100)
        if float(asks[-1][0]) >= asks_price or float(bids[-1][0]) <= bids_price:
            raise Exception(
                "Asks/Bids price for the required percentage not prenet in depth"
            )

        # Compute total qty for the require percentage prices and the ratio
        ask_qty = sum(
            [
                float(ask[1]) * float(ask[0])
                for ask in asks
                if float(ask[0]) <= asks_price
            ]
        )
        bid_qty = sum(
            [
                float(bid[1]) * float(bid[0])
                for bid in bids
                if float(bid[0]) >= bids_price
            ]
        )
        bid_ask_ratio = (bid_qty - ask_qty) / (bid_qty + ask_qty) * 100

        self.log.debug(
            f"{utl.BLUE(symbolName)}({percentage})\tBids:{utl.GREEN(bids_price)}\tQty:{utl.GREEN(bid_qty)}\tAsks:{utl.RED(asks_price)}\tQty:{utl.RED(ask_qty)}\tMRD({bid_ask_ratio})"
        )
        return bid_ask_ratio

    def getOrderStatus(self, symbolName: str, orderId: int) -> str:
        return self.get_order(symbolName=symbolName, orderId=orderId).get("status")

    def cancel_order(self, symbolName: str, orderId: int):
        return RUC(self.client.cancel_order(symbol=symbolName, orderId=orderId))

    def order_limit_sell(
        self, symbolName: str, qty: float, sellPrice: float, recvWindow=1000
    ) -> dict:
        return RUC(
            self.client.order_limit_sell(
                symbol=symbolName, quantity=qty, price=sellPrice, recvWindow=recvWindow
            )
        )

    def order_limit_buy(
        self, symbolName: str, qty: float, buyPrice: float, recvWindow=1000
    ) -> dict:
        return RUC(
            self.client.order_limit_buy(
                symbol=symbolName, quantity=qty, price=buyPrice, recvWindow=recvWindow
            )
        )

    def createStopLossSellOrder(
        self, symbolName: str, qty: float, stopPrice: float, limitPrice: float
    ) -> dict:
        return RUC(
            self.client.create_order(
                symbol=symbolName,
                side="SELL",
                type="STOP_LOSS_LIMIT",
                timeInForce="GTC",
                quantity=qty,
                stopPrice=stopPrice,
                price=limitPrice,
            )
        )

    def createOCOSellOrder(
        self,
        symbolName: str,
        qty: float,
        gainPrice: float,
        stopPrice: float,
        stoplimitPrice: float,
    ) -> dict:
        return RUC(
            self.client.create_oco_order(
                symbol=symbolName,
                side="SELL",
                #   type='STOP_LOSS_LIMIT',
                #   timeInForce='GTC',
                quantity=qty,
                stopPrice=stopPrice,
                price=gainPrice,
                stopLimitPrice=stoplimitPrice,
                stopLimitTimeInForce="GTC",
            )
        )
