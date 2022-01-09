from BinanceManager import MyBinanceManager
from .Order import LimitSellOrder
from .OrderHelpers import wait_order_fill
from python_log_indenter import IndentedLoggerAdapter
import traceback

_local_bm = MyBinanceManager('Sell')

#FIXME: THIS HAS NOT BEEN TESTED!!!!!!
def sell(symbolName: str, sell_price: float, qty: float,
         logger: IndentedLoggerAdapter) -> LimitSellOrder:
    """ Checks and create a sell-limit order only. Does not wait for order fill,
        However does normalize the price and qty. Returns Order.
        Raises exceptions when symbol info checks dont match!
        """
    logger.info(f' Selling ({qty}) {symbolName} @ ({sell_price}$)').push().add()
    symbol_info = _local_bm.get_symbol_info(symbolName=symbolName)

    # Normalize price & qty
    nprice = symbol_info.normalize_price(sell_price)
    nqty = symbol_info.normalize_quantity(qty)
    logger.info(f' Normalizing: Price({nprice}) Qty({nqty})')

    total = float(nprice) * float(nqty)
    # Check minNotion
    logger.info(f' MinNotion({total}) Required({symbol_info.minNotional})')
    if symbol_info.minNotional > total:
        raise Exception(f' MinNotional check failed!')

    # Check asset avialable to sell
    base_asset = symbol_info.baseAsset
    free_base = _local_bm.getFreeAsset(asset=base_asset)
    logger.info(f' {base_asset} Free({free_base}) Required({nqty})')
    if free_base < float(nqty):
        raise Exception(f' Not enough {base_asset}({free_base}) to sell')

    # Create sell order
    order = LimitSellOrder(
        _local_bm.order_limit_sell(symbolName=symbolName,
                                  qty=nqty,
                                  sellPrice=nprice))
    logger.info(f' LIMIT-SELL order created.').pop()
    return order


def sell_now(symbolName: str, qty: float,
            logger: IndentedLoggerAdapter) -> LimitSellOrder:
    """ Sell with the current ticker price(slightly lower)
        Returns Order if the sell succeeds, else None
        Raises an exception when sell order has an issue."""
    logger.info(f' Selling {symbolName} Quantity({qty})').push().add()

    while (True):
        # Sell with price slightly lower than current ticker price
        sell_price = _local_bm.getSymbolTickerPrice(
            symbolName=symbolName) * 0.999
        try:
            order = sell(symbolName=symbolName, sell_price=sell_price, qty=qty)
            if wait_order_fill(order=order, log=logger):
                logger.pop()
                return order
        except Exception as e:
            logger.error(f'{e}').pop()
            traceback.print_exc()
            exit(0)