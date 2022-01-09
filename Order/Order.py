from .OrderBase import OrderBase
from binance.client import BaseClient
from ..Utils import *

LIMIT = BaseClient.ORDER_TYPE_LIMIT
BUY = BaseClient.SIDE_BUY
SELL = BaseClient.SIDE_SELL


class LimitOrder(OrderBase):
    def __init__(self, orderDict: dict):
        super().__init__(orderDict)
        assert(self.type == LIMIT), "LimitOrder not provided with order a limit order!"

class LimitBuyOrder(LimitOrder):
    def __init__(self, orderDict: dict):
        super().__init__(orderDict)
        assert(self.side == BUY), "LimitBuyOrder not provided with order a buy order!"

    @property
    def buyPrice(self) -> float:
        return self.price

class LimitSellOrder(LimitOrder):
    def __init__(self, orderDict: dict):
        super().__init__(orderDict)
        assert(self.side == SELL), "LimitSellOrder not provided with order a sell order!"

    @property
    def sellPrice(self) -> float:
        return self.price


# NOTE: DONOT DELETE!!!!!
# class Order:
#     def __init__(self, order: dict):
#         # tempalte order:
#         # {'symbol': 'UNIUSDT', 'orderId': 1113456128, 'orderListId': -1, 'clientOrderId': 'OCyvGN73WE3OCDnG5kNhXy', 'price': '28.63000000', 'origQty': '0.35000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'STOP_LOSS_LIMIT', 'side': 'SELL', 'stopPrice': '28.69000000', 'icebergQty': '0.00000000', 'time': 1630461225413, 'updateTime': 1630461225413, 'isWorking': False, 'origQuoteOrderQty': '0.00000000'}
#         log.debug(f'OrderData: {order}')
#         self.dict = order

#         # These values dont change
#         self.orderId = order.get('orderId')
#         self.symbolName = self.dict.get('symbol')
#         self.price = float(order.get('price'))
#         self.origQty = float(self.dict.get('origQty'))
#         self.type = order.get('type')
#         self.side = order.get('side')

#     def _get_updated_order(self):
#         """ Gets the updated order values """
#         self.dict = _local_bm.get_order(symbolName=self.symbolName,
#                                         orderId=self.orderId)
#         return self.dict

#     @property
#     def symbolInfo(self) -> Symbol:
#         return _local_bm.get_symbol_info(symbolName=self.symbolName)

#     @property
#     def executedQty(self):
#         return float(self._get_updated_order().get('executedQty'))

#     @property
#     def current_status(self):
#         """ Gets the status provided with the order dict """
#         return self.dict.get('status')

#     @property
#     def latest_status(self):
#         """ Updates and get latest status """
#         return self._get_updated_order().get('status')

#     @property
#     def isalive(self):
#         """ Returns True if the order is still live! """
#         return False if self.latest_status in [
#             'CANCELED', 'FILLED', 'REJECTED', 'EXPIRED'
#         ] else True

#     @property
#     def isFilled(self) -> bool:
#         return True if self.latest_status == 'FILLED' else False

#     @property
#     def invested(self) -> float:
#         return self.price * self.executedQty

#     @property
#     def change_percentage(self) -> float:
#         """ Change percent from price to current ticker price """
#         return change_percent(Initial=self.price,
#                            Final=_local_bm.getSymbolTickerPrice(
#                                symbolName=self.symbolName))

#     @property
#     def change_percentage_str(self) -> str:
#         """ coloured change percent from price to current ticker price """
#         return color(self.change_percentage)

#     def __str__(self):
#         return f'orderId({self.orderId}) {self.symbolName} {self.type}-{self.side} Status({self.current_status}) Price({self.price}) origQty({self.origQty}) executedQty({self.dict.get("executedQty")})'

#     def telegram_msg(self) -> str:
#         """ Constructs a telegram message """
#         # https://stackoverflow.com/a/61225235
#         return f'{self.type}-{self.side}: {self.symbolName}\nPrice: {self.price}\norigQty: {self.origQty}\nStatus({self.latest_status})'.replace(
#             '_', '-')

#     def cancel(self):
#         if self.latest_status != 'CANCELED':
#             _local_bm.cancel_order(symbolName=self.symbolName,
#                                    orderId=self.orderId)
#             log.info(f' OrderId({self.orderId}): Cancelled')
#         else:
#             log.info(f' OrderId({self.orderId}): Already Canceleld!')

#     def wait_order_status(self, required_status: str) -> bool:
#         """ Waits for order status to change to required_status.
#             Returns True if successful else False """
#         log.info(
#             f' Waiting for order status({self.latest_status}) to change to ({required_status})'
#         ).push().add()
#         timer_end = time() + Constants.ORDER_WAIT_TIMER
#         while time() < timer_end:
#             # status = _local_bm.getOrderStatus(symbolName=symbolName,
#             #                                   orderId=orderId)
#             if self.latest_status == required_status:
#                 log.info(f' Order Status changed: {required_status}').pop()
#                 return True
#             log.info(f' Waiting Order Status: {required_status}')
#             sleep(0.5)
#         # Timer expired, cancel order!
#         log.info(' Failed: Timer Expired!').pop()
#         return False

#     def wait_order_fill(self) -> bool:
#         """ Waits for order status to be FILLED. Returns True
#             if successful else cancels the order and returns False """
#         if self.wait_order_status(required_status='FILLED'):
#             return True
#         self.cancel()
#         return False

#     def set_stopsloss_sell(self, stoploss_percentage: float) -> Order:
#         """ Sets a stoploss at a price lower than given stoploss percentage """
#         log.info(
#             f' Creating Stop-loss-limit-sell order with stoploss({stoploss_percentage}%)'
#         ).push().add()
#         if self.side != 'BUY' or self.latest_status != 'FILLED':
#             log.error(
#                 f' Order side({self.side}) must be BUY and status({self.latest_status}) must be FILLED.'
#             ).pop()
#             exit(0)
#         assert (stoploss_percentage >=
#                 0.0), "Stoploss percentage must be positive"

#         # Compute stoploss values
#         stopPrice = self.price * ((100.0 - stoploss_percentage) / 100.0)
#         limitPrice = stopPrice * 0.998
#         symbolInfo = self.symbolInfo
#         nstopPrice = symbolInfo.normalize_price(stopPrice)
#         nlimitPrice = symbolInfo.normalize_price(limitPrice)
#         nqty = symbolInfo.normalize_quantity(self.executedQty)

#         # Check minnotional is satisfied
#         total = float(nqty) * float(nlimitPrice)
#         if not symbolInfo.is_minNotional_fullfilled(priceQty=total):
#             log.error(f' MinNotion({total}) Required({symbolInfo.minNotional})'
#                       ).pop()
#             exit(0)

#         # This returns a different type of response
#         # {'symbol': 'UNIUSDT', 'orderId': 1113463912, 'orderListId': -1, 'clientOrderId': 'df2ExmPSpMG2cNBhlXSAYV', 'transactTime': 1630461524925}
#         # Therefore, we need to use the orderId to get properly initialize our Order class
#         orderId = _local_bm.createStopLossSellOrder(
#             symbolName=self.symbolName,
#             qty=nqty,
#             stopPrice=nstopPrice,
#             limitPrice=nlimitPrice).get('orderId')
#         log.info(
#             f' Created: StopPrice({nstopPrice}) LimitPrice({nlimitPrice}) Qty({self.origQty})'
#         ).pop()
#         return SLOrder(
#             _local_bm.get_order(symbolName=self.symbolName, orderId=orderId))

#     def set_limit_sell(self, gain_percentage: float) -> Order:
#         log.info(f' Creating limit-sell order with gain({gain_percentage}%)'
#                  ).push().add()
#         if self.side != 'BUY' or self.latest_status != 'FILLED':
#             log.error(
#                 f' Order side({self.side}) must be BUY and status({self.latest_status}) must be FILLED.'
#             ).pop()
#             exit(0)
#         assert (gain_percentage >= 0.0), "Gain percentage must be positive"
#         gainPrice = self.price * ((100.0 + gain_percentage) / 100.0)
#         symbolInfo = self.symbolInfo
#         ngainPrice = symbolInfo.normalize_price(gainPrice)
#         nqty = symbolInfo.normalize_quantity(self.executedQty)
#         # Check minNotional is satisfied: not required
#         order = _local_bm.order_limit_sell(symbolName=self.symbolName,
#                                            qty=nqty,
#                                            sellPrice=ngainPrice)
#         log.info(
#             f' Created: GainPrice({ngainPrice}) Qty({self.origQty})').pop()
#         return Order(order)

#     def set_oco_sell(self, gain_percentage: float,
#                      stoploss_percentage: float) -> OCOOrder:
#         """ Sets an oco sell order """
#         log.info(
#             f'Creating Stop-loss-limit-sell order with gain({gain_percentage}%) and stoploss({stoploss_percentage}%)'
#         ).push().add()
#         if self.side != 'BUY' or self.latest_status != 'FILLED':
#             log.error(
#                 f' Order side({self.side}) must be BUY and status({self.latest_status}) must be FILLED.'
#             ).pop()
#             exit(0)
#         assert (stoploss_percentage >=
#                 0.0), "Stoploss percentage must be positive"
#         assert (gain_percentage >= 0.0), "Gain percentage must be positive"

#         # Compute values
#         gainPrice = self.price * ((100.0 + gain_percentage) / 100.0)
#         stopPrice = self.price * ((100.0 - stoploss_percentage) / 100.0)
#         stoplimitPrice = stopPrice * 0.998
#         symbolInfo = self.symbolInfo
#         ngainPrice = symbolInfo.normalize_price(gainPrice)
#         nstopPrice = symbolInfo.normalize_price(stopPrice)
#         nstoplimitPrice = symbolInfo.normalize_price(stoplimitPrice)
#         nqty = symbolInfo.normalize_quantity(self.executedQty)

#         # Check minNotional is satisfied
#         total = float(nqty) * float(stoplimitPrice)
#         if not symbolInfo.is_minNotional_fullfilled(priceQty=total):
#             log.error(f' MinNotion({total}) Required({symbolInfo.minNotional})'
#                       ).pop()
#             exit(0)

#         # This returns something like:
#         # {'orderListId': 43007143, 'contingencyType': 'OCO', 'listStatusType': 'EXEC_STARTED', 'listOrderStatus': 'EXECUTING', 'listClientOrderId': '5w0X3zsCRIGaU5qrlS2leW',
#         # 'transactionTime': 1630464045385, 'symbol': 'UNIUSDT',
#         # 'orders': [{'symbol': 'UNIUSDT', 'orderId': 1113540529, 'clientOrderId': '17gaexl7kTkQQF3vKosZKr'},
#         # {'symbol': 'UNIUSDT', 'orderId': 1113540530, 'clientOrderId': 'jIz0XOaN4MkuDizhEE2J71'}], 'orderReports': [{'symbol': 'UNIUSDT', 'orderId': 1113540529, 'orderListId': 43007143, 'clientOrderId': '17gaexl7kTkQQF3vKosZKr',
#         # 'transactTime': 1630464045385, 'price': '28.63000000', 'origQty': '0.35000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty':
#         # '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'STOP_LOSS_LIMIT', 'side': 'SELL', 'stopPrice': '28.69000000'},
#         # {'symbol': 'UNIUSDT', 'orderId': 1113540530, 'orderListId': 43007143, 'clientOrderId': 'jIz0XOaN4MkuDizhEE2J71', 'transactTime': 1630464045385, 'price': '30.47000000', 'origQty': '0.35000000', 'executedQty': '0.00000000', 'cummulativeQuoteQty': '0.00000000', 'status': 'NEW', 'timeInForce': 'GTC', 'type': 'LIMIT_MAKER', 'side': 'SELL'}]}
#         order = _local_bm.createOCOSellOrder(
#             symbolName=self.symbolName,
#             qty=nqty,
#             stopPrice=nstopPrice,
#             stoplimitPrice=nstoplimitPrice,
#             gainPrice=ngainPrice,
#         )
#         log.info(
#             f' Created: GainPrice({ngainPrice}) StopPrice({nstopPrice}) StopLimitPrice({stoplimitPrice}) Qty({nqty})'
#         ).pop()
#         return OCOOrder(order)


# class SLOrder(Order):
#     """ Stoploss order basics """
#     def __init__(self, order: dict):
#         super().__init__(order)
#         self.stopPrice = float(order.get('stopPrice'))

#     def __str__(self):
#         return f'{super().__str__()} StopPrice({self.stopPrice})'

#     def telegram_msg(self) -> str:
#         """ Sends a telegram push """
#         return super().telegram_msg(
#         ) + f'\nStopPrice: {self.stopPrice}'.replace('_', '-')


# class OCOOrder:
#     """ OCO order basic, oco order does not itself have an orderId, rather 2 separate orders both of which are linked using the orderListId
#     Therefore, here, we save the complete dict and get the orders independently. """
#     def __init__(self, order: dict):
#         self.o = order
#         pass

#     @property
#     def limitOrder(self) -> Order:
#         return Order(
#             next(x for x in self.o.get('orderReports')
#                  if x.get('type') == 'LIMIT_MAKER'))

#     @property
#     def stoplossOrder(self) -> SLOrder:
#         return SLOrder(
#             next(x for x in self.o.get('orderReports')
#                  if x.get('type') == 'STOP_LOSS_LIMIT'))

#     def __str__(self):
#         return f'{self.limitOrder} & {self.stoplossOrder}'

#     def telegram_msg(self) -> str:
#         """ Generate a telegram message """
#         return f'OCO\n{self.limitOrder.telegram_msg()}\n{self.stoplossOrder.telegram_msg()}'.replace(
#             '_', '-')

#     def cancel(self):
#         log.info(f'Cancelling OCO order:').push().add()
#         self.limitOrder.cancel()
#         self.stoplossOrder.cancel()
#         log.pop()