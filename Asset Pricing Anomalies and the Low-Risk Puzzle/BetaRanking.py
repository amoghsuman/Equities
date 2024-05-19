import backtrader as bt
import backtrader.feeds as btfeeds
import pandas as pd

class BetaRanking(bt.Strategy):
    params = (
        ('lookback', 252),
        ('rebalance_freq', 21),
        ('num_long', 10),
        ('num_short', 10)
    )

    def __init__(self):
        self.betas = {}
        self.rankings = []
        self.rebalance_day = 0
        # Compute beta for each stock
        for d in self.datas:
            self.betas[d._name] = bt.indicators.Beta(d, self.data0, period=self.params.lookback)

    def next(self):
        self.rebalance_day += 1
        if self.rebalance_day % self.params.rebalance_freq != 0:
            return
        self.rankings = sorted(
            self.datas,
            key=lambda d: self.betas[d._name][0]
        )
        longs = self.rankings[:self.params.num_long]
        shorts = self.rankings[-self.params.num_short:]
        for d in longs:
            self.order_target_percent(d, target=1.0 / self.params.num_long)
        for d in shorts:
            self.order_target_percent(d, target=-1.0 / self.params.num_short)
        for d in self.datas:
            if d not in longs and d not in shorts:
                self.order_target_percent(d, target=0.0)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # Add strategy
    cerebro.addstrategy(BetaRanking)

    # Load CRSP database
    # Replace this part with your actual CRSP data
    for stock_data in CRSP_data:
        data = btfeeds.PandasData(dataname=stock_data)
        cerebro.adddata(data)

    # Load MSCI US Equity Index data
    msci_data = btfeeds.PandasData(dataname=pd.read_csv('msci_us_equity_index.csv', parse_dates=['date'], index_col='date'))
    cerebro.adddata(msci_data, name='msci_us_equity_index')

    # Set initial capital and run
    cerebro.broker.setcash(100000.0)
    cerebro.run()
