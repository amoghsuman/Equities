import backtrader as bt

class MomentumStyleRotation(bt.Strategy):
    params = (
        ("momentum_period", 12),
    )

    def __init__(self):
        self.etfs = self.datas
        self.momentum = [bt.indicators.Momentum(e, period=self.params.momentum_period) for e in self.etfs]

    def next(self):
        long_etf = max(zip(self.momentum, self.etfs), key=lambda x: x[0][0])
        short_etf = min(zip(self.momentum, self.etfs), key=lambda x: x[0][0])
        for etf in self.etfs:
            if etf == long_etf[1]:
                self.order_target_percent(etf, target=1)
            elif etf == short_etf[1]:
                self.order_target_percent(etf, target=-1)
            else:
                self.order_target_percent(etf, target=0)

if __name__ == "__main__":
    cerebro = bt.Cerebro()
    # Add six Russell ETFs data feeds
    for etf_code in ["ETF1", "ETF2", "ETF3", "ETF4", "ETF5", "ETF6"]:
        data = bt.feeds.YahooFinanceData(dataname=etf_code, fromdate="2000-01-01", todate="2021-12-31")
        cerebro.adddata(data)
    cerebro.addstrategy(MomentumStyleRotation)
    cerebro.broker.setcash(100000)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.run()
