from BinanceManager import MyBinanceManager
from .Order import OrderBase
from .Constants import ORDER_WAIT_TIMER
from Utils import *
from time import sleep
from python_log_indenter import IndentedLoggerAdapter

_local_bm = MyBinanceManager('OrderHelpers')


def cancel(order: OrderBase, log: IndentedLoggerAdapter):
    """ Cancels an order, that has not been already cancelled """
    if order.latestStatus != 'CANCELED':
        _local_bm.cancel_order(symbolName=order.symbolName,
                               orderId=order.orderId)
        log.info(f' OrderId({order.orderId}): Cancelled')
    else:
        log.info(f' OrderId({order.orderId}): Already Canceleld!')


def wait_order_status(order: OrderBase, requiredStatus: str,
                      log: IndentedLoggerAdapter) -> bool:
    """ Waits for order status to change to required_status.
            Returns True if successful else False """
    log.info(
        f' Waiting for order status({order.latestStatus}) to change to ({requiredStatus})'
    ).push().add()
    timer_end = time() + ORDER_WAIT_TIMER
    while time() < timer_end:
        # status = _local_bm.getOrderStatus(symbolName=symbolName,
        #                                   orderId=orderId)
        if order.latestStatus == requiredStatus:
            log.info(f' Order Status changed: {requiredStatus}').pop()
            return True
        log.info(f' Waiting Order Status: {requiredStatus}')
        sleep(0.5)
    # Timer expired, cancel order!
    log.info(' Failed: Timer Expired!').pop()
    return False


def wait_order_fill(order: OrderBase, log: IndentedLoggerAdapter) -> bool:
    """ Waits for order status to be FILLED. Returns True
            if successful else cancels the order and returns False """
    if wait_order_status(order=order, requiredStatus='FILLED'):
        return True
    cancel(order=order, log=log)
    return False

# NOTE: DONOT DELETE!!!!!
# def set_stopsloss_sell(self, stoploss_percentage: float) -> Order:
#     """ Sets a stoploss at a price lower than given stoploss percentage """
#     log.info(
#         f' Creating Stop-loss-limit-sell order with stoploss({stoploss_percentage}%)'
#     ).push().add()
#     if self.side != 'BUY' or self.latest_status != 'FILLED':
#         log.error(
#             f' Order side({self.side}) must be BUY and status({self.latest_status}) must be FILLED.'
#         ).pop()
#         exit(0)
#     assert (stoploss_percentage >= 0.0), "Stoploss percentage must be positive"

#     # Compute stoploss values
#     stopPrice = self.price * ((100.0 - stoploss_percentage) / 100.0)
#     limitPrice = stopPrice * 0.998
#     symbolInfo = self.symbolInfo
#     nstopPrice = symbolInfo.normalize_price(stopPrice)
#     nlimitPrice = symbolInfo.normalize_price(limitPrice)
#     nqty = symbolInfo.normalize_quantity(self.executedQty)

#     # Check minnotional is satisfied
#     total = float(nqty) * float(nlimitPrice)
#     if not symbolInfo.is_minNotional_fullfilled(priceQty=total):
#         log.error(
#             f' MinNotion({total}) Required({symbolInfo.minNotional})').pop()
#         exit(0)

#     # This returns a different type of response
#     # {'symbol': 'UNIUSDT', 'orderId': 1113463912, 'orderListId': -1, 'clientOrderId': 'df2ExmPSpMG2cNBhlXSAYV', 'transactTime': 1630461524925}
#     # Therefore, we need to use the orderId to get properly initialize our Order class
#     orderId = _local_bm.createStopLossSellOrder(
#         symbolName=self.symbolName,
#         qty=nqty,
#         stopPrice=nstopPrice,
#         limitPrice=nlimitPrice).get('orderId')
#     log.info(
#         f' Created: StopPrice({nstopPrice}) LimitPrice({nlimitPrice}) Qty({self.origQty})'
#     ).pop()
#     return SLOrder(
#         _local_bm.get_order(symbolName=self.symbolName, orderId=orderId))


# def set_limit_sell(self, gain_percentage: float) -> Order:
#     log.info(f' Creating limit-sell order with gain({gain_percentage}%)').push(
#     ).add()
#     if self.side != 'BUY' or self.latest_status != 'FILLED':
#         log.error(
#             f' Order side({self.side}) must be BUY and status({self.latest_status}) must be FILLED.'
#         ).pop()
#         exit(0)
#     assert (gain_percentage >= 0.0), "Gain percentage must be positive"
#     gainPrice = self.price * ((100.0 + gain_percentage) / 100.0)
#     symbolInfo = self.symbolInfo
#     ngainPrice = symbolInfo.normalize_price(gainPrice)
#     nqty = symbolInfo.normalize_quantity(self.executedQty)
#     # Check minNotional is satisfied: not required
#     order = _local_bm.order_limit_sell(symbolName=self.symbolName,
#                                        qty=nqty,
#                                        sellPrice=ngainPrice)
#     log.info(f' Created: GainPrice({ngainPrice}) Qty({self.origQty})').pop()
#     return Order(order)


# def set_oco_sell(self, gain_percentage: float,
#                  stoploss_percentage: float) -> OCOOrder:
#     """ Sets an oco sell order """
#     log.info(
#         f'Creating Stop-loss-limit-sell order with gain({gain_percentage}%) and stoploss({stoploss_percentage}%)'
#     ).push().add()
#     if self.side != 'BUY' or self.latest_status != 'FILLED':
#         log.error(
#             f' Order side({self.side}) must be BUY and status({self.latest_status}) must be FILLED.'
#         ).pop()
#         exit(0)
#     assert (stoploss_percentage >= 0.0), "Stoploss percentage must be positive"
#     assert (gain_percentage >= 0.0), "Gain percentage must be positive"

#     # Compute values
#     gainPrice = self.price * ((100.0 + gain_percentage) / 100.0)
#     stopPrice = self.price * ((100.0 - stoploss_percentage) / 100.0)
#     stoplimitPrice = stopPrice * 0.998
#     symbolInfo = self.symbolInfo
#     ngainPrice = symbolInfo.normalize_price(gainPrice)
#     nstopPrice = symbolInfo.normalize_price(stopPrice)
#     nstoplimitPrice = symbolInfo.normalize_price(stoplimitPrice)
#     nqty = symbolInfo.normalize_quantity(self.executedQty)

#     # Check minNotional is satisfied
#     total = float(nqty) * float(stoplimitPrice)
#     if not symbolInfo.is_minNotional_fullfilled(priceQty=total):
#         log.error(
#             f' MinNotion({total}) Required({symbolInfo.minNotional})').pop()
#         exit(0)

#     # This returns something like:
#     # {'orderListId': 43007143, 'contingencyType': 'OCO', 'listStatusType': 'EXEC_STARTED', 'listOrderStatus': 'EXECUTING', 'listClientOrderId': '5w0X3zsCRIGaU5qrlS2leW',
#     # 'transactionTime': 1630464045385, 'symbol': 'UNIUSDT',
#     # 'orders': [{'symbol': 'UNIUSDT', 'orderId': 1113540529, 'clientOrderId': '17gaexl7kTkQQF3vKosZKr'},
#     # {'symbol': 'UNIUSDT', 'orderId': 1113540530, 'clientOrderId': 'jIz0XOaN4MkuDizhEE2J71'}], 'orderReports': [{'symbol': 'UNIUSDT', 'orderId': 1113540529, 'orderListId': 43007143, 'clientOrderId': '17gaexl7kTkQQF3vKosZKr',
#     # 'transactTime': 1630464045385, 'price': '28.63000000', 'origQty': '0.35000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty':
#     # '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'STOP_LOSS_LIMIT', 'side': 'SELL', 'stopPrice': '28.69000000'},
#     # {'symbol': 'UNIUSDT', 'orderId': 1113540530, 'orderListId': 43007143, 'clientOrderId': 'jIz0XOaN4MkuDizhEE2J71', 'transactTime': 1630464045385, 'price': '30.47000000', 'origQty': '0.35000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT_MAKER', 'side': 'SELL'}]}
#     order = _local_bm.createOCOSellOrder(
#         symbolName=self.symbolName,
#         qty=nqty,
#         stopPrice=nstopPrice,
#         stoplimitPrice=nstoplimitPrice,
#         gainPrice=ngainPrice,
#     )
#     log.info(
#         f' Created: GainPrice({ngainPrice}) StopPrice({nstopPrice}) StopLimitPrice({stoplimitPrice}) Qty({nqty})'
#     ).pop()
#     return OCOOrder(order)
