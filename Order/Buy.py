from BinanceManager import MyBinanceManager
from .Order import LimitBuyOrder
from .OrderHelpers import wait_order_fill
from python_log_indenter import IndentedLoggerAdapter

_local_bm = MyBinanceManager('Buy')

def buy(symbolName:str, buy_price:float, qty:float,
        logger: IndentedLoggerAdapter) -> LimitBuyOrder:
    """ Checks and create a buy-limit order only. Does not wait for order fill,
        However does normalize the price and qty. Returns Order.
        Raises exceptions when symbol info checks dont match!
        """
    logger.info(f' Buying ({qty}) {symbolName} @ ({buy_price}$)').push().add()
    symbol_info = _local_bm.get_symbol_info(symbolName=symbolName)

    # Normalize price & qty
    nprice = symbol_info.normalize_price(buy_price)
    nqty = symbol_info.normalize_quantity(qty)
    logger.info(f' Normalizing: Price({nprice}) Qty({nqty})')

    total = float(nprice) * float(nqty)
    # Check minNotion
    logger.info(f' MinNotion({total}) Required({symbol_info.minNotional})')
    if symbol_info.minNotional > total:
        raise Exception(f' MinNotional check failed!')

    # Check asset avialable
    free_usdt = _local_bm.getFreeAsset(asset='USDT')
    logger.info(f' USDT Free({free_usdt}) Required({total})')
    if free_usdt < total:
        raise Exception(f' Not enough USDT({free_usdt}) to buy')

    # Create order
    order = LimitBuyOrder(_local_bm.order_limit_buy(symbolName=symbolName, qty=nqty, buyPrice=nprice))
    logger.info(f' LIMIT-BUY order created.').pop()
    return order

def buy_now(symbolName:str, capital:float, logger: IndentedLoggerAdapter) -> LimitBuyOrder:
    """ Buy with the current ticker price(slightly higher)
        Returns Order if the buy succeeds, else None
        Raises an exception when buy order has an issue."""
    logger.info(f' Buying {symbolName} with Capital({capital})').push().add()

    while(True):
        # Buy with price slightly higher than current ticker price
        buy_price = _local_bm.getSymbolTickerPrice(symbolName=symbolName) * 1.001
        qty = capital / buy_price
        order = buy(symbolName=symbolName, buy_price=buy_price, qty=qty)
        if wait_order_fill(order=order, log=logger):
            logger.info(f' Buys succeeded: OrderId({order.orderId})')
            logger.pop()
            return order
