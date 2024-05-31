from ..Utils import BLUE
from binance.helpers import round_step_size


class Symbol:
    # https://python-binance.readthedocs.io/en/latest/binance.html#binance.client.Client.get_symbol_info
    def __init__(self, SymbolInfo: dict):
        self._d = SymbolInfo
        self.name = SymbolInfo.get("symbol")
        self.baseAsset = SymbolInfo.get("baseAsset")
        self.quoteAsset = SymbolInfo.get("quoteAsset")
        self.quotePrecison = int(SymbolInfo.get("quotePrecision"))
        self.hasLimitOrder = True if "LIMIT" in SymbolInfo.get("orderTypes") else False

        for f in SymbolInfo.get("filters"):
            if f.get("filterType") == "PRICE_FILTER":
                self.maxPrice = float(f.get("maxPrice"))
                self.minPrice = float(f.get("minPrice"))
                self.tickSize = float(f.get("tickSize"))

            elif f.get("filterType") == "LOT_SIZE":
                self.minQty = float(f.get("minQty"))
                self.maxQty = float(f.get("maxQty"))
                self.stepSize = float(f.get("stepSize"))

            elif f.get("filterType") == "MIN_NOTIONAL":
                self.minNotional = float(f.get("minNotional"))

    def symbol_str(self):
        return f"Symbol({BLUE(self.name)}) baseAsset({self.baseAsset}) quoteAsset({self.quoteAsset}) quotePrecison({self.quotePrecison})"

    def __str__(self):
        return f"Symbol({BLUE(self.name)}) baseAsset({self.baseAsset}) quoteAsset({self.quoteAsset}) quotePrecison({self.quotePrecison})"

    def normalize_price(self, price: float) -> str:
        # FIXME: these should be handled properly
        assert price > self.minPrice, "Price less than min price of symbol"
        assert price < self.maxPrice, "Price less than min price of symbol"
        # Subtract a tick size, just to be sure
        price = round_step_size(quantity=price - self.tickSize, step_size=self.tickSize)
        # returns float as string to avoid scientific notion coversion!
        return f"{price:.{int(self.quotePrecison)}f}"[:9]

    def normalize_quantity(self, qty: float) -> str:
        # FIXME: these should be handled properly
        assert qty > self.minQty, "Quantity less than min Quantity of symbol"
        assert qty < self.maxQty, "Quantity less than min Quantity of symbol"
        # Subtract a step size, just to be sure
        qty = round_step_size(quantity=qty - self.stepSize, step_size=self.stepSize)
        # returns float as string to avoid scientific notion coversion!
        return f"{qty:.{int(self.quotePrecison)}f}"[:9]

    def is_minNotional_fullfilled(self, priceQty: float) -> bool:
        """Check if the order fullfills the miin notional (Price*Qty) value"""
        return True if priceQty >= self.minNotional else False

    def order_checks_okay(self, price: float, qty: float) -> bool:
        # FIXME: not required for now!
        # the normalize function returns strs, so we need to convert to float before checking
        price = float(price)
        qty = float(qty)
        okay = True
        if not (price > self.minPrice and price < self.maxPrice):
            print("Price filter not satisfied")
            okay = False
        if not (qty > self.minQty and qty < self.maxQty):
            print("Qty filter not satisfied")
            okay = False
        if not (price * qty) > self.minNotional:
            print("MinNotioanl not according satisfied")
            okay = False
        return okay
