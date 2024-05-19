import backtrader as bt
import pandas as pd

class CashBasedOperatingProfitability(bt.Strategy):
    params = (
        ('deciles', 10),
    )

    def __init__(self):
        self.ranker = None

    def next(self):
        if self.ranker is not None:
            self.ranker.cancel()
        self.ranker = self.datas[0].close[0]

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Margin]:
            self.ranker = None

    def prenext(self):
        self.next()

    def rebalance_portfolio(self):
        market_caps = {data: data.market_cap[0] for data in self.datas}
        big_stocks = sorted(self.datas, key=lambda d: market_caps[d], reverse=True)[:len(self.datas)//2]
        op_profits = {data: data.sales[0] - data.cogs[0] - data.sga[0] for data in big_stocks}
        cash_based_op_profits = {data: op_profits[data] - data.accruals[0] for data in big_stocks}
        sorted_by_cbop = sorted(big_stocks, key=lambda d: cash_based_op_profits[d], reverse=True)
        long_stocks = sorted_by_cbop[:len(sorted_by_cbop)//self.params.deciles]
        short_stocks = sorted_by_cbop[-len(sorted_by_cbop)//self.params.deciles:]
        for data in self.datas:
            if data in long_stocks:
                self.order_target_percent(data, target=market_caps[data] / sum(market_caps.values()))
            elif data in short_stocks:
                self.order_target_percent(data, target=-market_caps[data] / sum(market_caps.values()))
            else:
                self.order_target_percent(data, target=0.0)

    def next_open(self):
        self.rebalance_portfolio()

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(CashBasedOperatingProfitability)
    # Add data feeds for NYSE, Amex, NASDAQ-traded firms (excluding non-common shares)
    # ...
    cerebro.run()
    cerebro.plot()
