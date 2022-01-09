from .BinanceManager import MyBinanceManager
from .Order import OrderBase
from .Utils import get_date_str, change_percent, color
from typing import List
import pandas as pd
import tqdm

# Local binance manager
_local_bm = MyBinanceManager('PortfolioManager')
EUR2USDT = _local_bm.getSymbolTickerPrice(symbolName='EURUSDT')

class Asset:
    """ Class to define a simple asset. Only the fields that we require """

    def __init__(self, asset: dict) -> None:
        self.name = asset.get('asset')
        self.free = float(asset.get('free'))
        self.locked = float(asset.get('locked'))

    @property
    def total(self):
        return self.free + self.locked

    def __str__(self):
        return f'Asset({self.name}) free({self.free}) locked({self.locked})'


class AssetAvgPrice:
    def __init__(self, asset: str):
        self.asset = asset
        self.qty = 0.0
        self.buy_avg = 0.0

    @property
    def total(self):
        return self.qty * self.buy_avg

    def addOrder(self, order: OrderBase):
        # Get the quote asset
        quote_asset = order.symbolName.replace(self.asset, '', 1)

        # Ensure that symbol name is 'EUR' or 'USDT'
        if quote_asset not in ['EUR', 'USDT']:
            return

        # Determine if its EUR, then add the coversion factor
        factor = 1.0
        if quote_asset == 'EUR':
            factor = EUR2USDT

        # Enure that the order is filled, others can be cancelled, expired, closed etc....
        if order.status != 'FILLED':
            return

        executed_qty = order.executedQty
        if order.side == 'SELL':
            self.qty -= executed_qty
        elif order.side == 'BUY':
            total = executed_qty * order.price * factor + self.total
            self.qty += executed_qty
            self.buy_avg = total / self.qty

    def __str__(self):
        return f'Asset({self.asset}) Qty({self.qty}) BuyAvgPrice({self.buy_avg}$)'


def get_asset_avg_buy_price(asset: str) -> float:
    assetAvg = AssetAvgPrice(asset)
    orders = []
    # Get all usdt and eur orders and sorted with time
    for order in _local_bm.get_all_orders(symbolName=asset + 'USDT'):
        orders.append(order)
    try:
        for order in _local_bm.get_all_orders(symbolName=asset + 'EUR'):
            orders.append(order)
    except Exception:
        pass
    orders.sort(key=lambda x: x['time'])

    # Traverse the orders
    for order in orders:
        assetAvg.addOrder(OrderBase(order))
    return assetAvg.buy_avg


def _get_all_assets() -> List[Asset]:
    return [Asset(asset=asset) for asset in _local_bm.getAccountBalances()]


class PortfolioManager:
    def __init__(self):
        self.depositedFiatUSD = PortfolioManager.getDepositedFiatUSD()
        self.completePortfolio = PortfolioManager.getCompletePortfolio()

    @property
    def depositedFiatEUR(self) -> float:
        return self.depositedFiatUSD / EUR2USDT

    @property
    def prunedPortfolio(self) -> pd.DataFrame:
        """ returns the dataframe where assets whose current worth is less than 10$ are removed """
        idx_to_prune = [idx for idx, row in self.completePortfolio.iterrows() if float(row['CurrentWorth']) < 10.0]
        return self.completePortfolio.drop(index=idx_to_prune)

    @property
    def investedUSD(self) -> float:
        """ Total money invested in the coins """
        return self.completePortfolio['TotalInvested'].sum()

    @property
    def investedEUR(self) -> float:
        """ Total money invested in the coins """
        return self.investedUSD / EUR2USDT

    @property
    def currentUSD(self) -> float:
        """ Current worth of the invested """
        return self.completePortfolio['CurrentWorth'].sum()

    def print_portfolio(self) -> None:
        """ Prints the pruned portfolio with styling """
        df = self.prunedPortfolio.copy(deep=True)
        # Formatting of the individual columns
        format_mapping={
            'Qty': '{:.2f}',
            'Free': '{:.2f}',
            'Portfolio%' : '{:.2f}%',
            'AvgBuyPrice' : '{:.5f}$',
            'CurrentPrice' : '{:.5f}$',
            'TotalInvested' : '{:.1f}$',
            'CurrentWorth' : '{:.1f}$',
        }
        for key, value in format_mapping.items():
            df[key] = df[key].apply(value.format)

        print(df)

    # Static functions
    @staticmethod
    def getCurrentAssets() -> List[Asset]:
        return [asset for asset in _get_all_assets() if asset.total != 0.0]

    @staticmethod
    def getDepositedFiatUSD() -> float:
        """ Retruns total deposited usdt
            https://binance-docs.github.io/apidocs/spot/en/#get-fiat-deposit-withdraw-history-user_data
        """
        def get_eur_day_price(time: int) -> float:
            # Gets the cLose price of the day
            date = get_date_str(deposit.get("updateTime"))
            return _local_bm.get_historical_klines(
                symbolName='EURUSDT',
                interval='1d',
                startTime=date).df.at[0,'Close']

        total = 0.0
        deposits = _local_bm.getFiatDepositHistory().get('data')
        for deposit in deposits:
            orderTime = get_date_str(deposit.get("updateTime"))
            # Continue if deposit fails
            if deposit.get('status') != 'Successful':
                continue
            total += float(deposit.get('amount')) * get_eur_day_price(
                orderTime) if deposit.get('fiatCurrency') == 'EUR' else float(
                    deposit.get('amount'))
        return total

    @staticmethod
    def getCompletePortfolio() -> pd.DataFrame:
        assets = PortfolioManager.getCurrentAssets()
        assets_list = list()
        for i in tqdm.tqdm(range(len(assets))):
            asset = assets[i]
            if asset.name == 'USDT':
                avg = ticker_price = 1.0
            else:
                avg = get_asset_avg_buy_price(asset=asset.name)
                ticker_price = _local_bm.getSymbolTickerPrice(asset.name + "USDT")
                # free = asset.free
            total = asset.total * avg
            if total == 0.0:
                continue

            change_str = color(change_percent(Initial=avg, Final=ticker_price)) + '%'
            current_value = asset.total * ticker_price
            assets_list.append(
                {
                    'Symbol': asset.name,
                    'Qty': asset.total,
                    'Free': asset.free,
                    'AvgBuyPrice': avg,
                    'TotalInvested': total,
                    'CurrentPrice': ticker_price,
                    'CurrentWorth': current_value,
                    'Change%': change_str,
                })
        # Create a df with all asset values
        columns = [
            'Symbol', 'Qty', 'Free', 'Portfolio%', 'AvgBuyPrice', 'TotalInvested', 'CurrentPrice', 'CurrentWorth', 'Change%',]
        df = pd.DataFrame(assets_list, columns=columns)
        # Determine the portfolio percentage per asset
        total_investment = df['TotalInvested'].sum()
        for index, row in df.iterrows():
            df.at[index, 'Portfolio%'] = row['TotalInvested'] / total_investment * 100
        # sort the df by CurrentWorth
        df.sort_values(by=['CurrentWorth'], ignore_index=True, ascending=False, inplace=True)
        return df