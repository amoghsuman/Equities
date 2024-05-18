import backtrader as bt
import backtrader.feeds as btfeeds
import datetime

class LotteryEffectStrategy(bt.Strategy):
    def __init__(self):
        self.inds = dict()
        for d in self.datas:
            self.inds[d] = dict()
            self.inds[d]['max_return'] = bt.indicators.Highest(d.close / d.close(-1) - 1, period=21)

    def next(self):
        max_returns = []
        for d in self.datas:
            max_returns.append((self.inds[d]['max_return'][0], d))

        max_returns.sort(key=lambda x: x[0])

        long_stocks = max_returns[:len(max_returns) // 10]
        short_stocks = max_returns[-(len(max_returns) // 10):]

        for _, d in long_stocks:
            self.order_target_percent(d, target=1 / len(long_stocks))

        for _, d in short_stocks:
            self.order_target_percent(d, target=-1 / len(short_stocks))

        for _, d in max_returns[len(long_stocks):-len(short_stocks)]:
            self.order_target_percent(d, target=0)

cerebro = bt.Cerebro()

data_path = 'path_to_your_data_directory'
tickers = ['NYSE', 'AMEX', 'NASDAQ']

for ticker in tickers:
    data = btfeeds.GenericCSVData(
        dataname=data_path + ticker + '.csv',
        dtformat=('%Y-%m-%d'),
        datetime=0,
        high=2,
        low=3,
        open=1,
        close=4,
        volume=5,
        openinterest=-1,
        reverse=False
    )
    cerebro.adddata(data)

cerebro.addstrategy(LotteryEffectStrategy)
cerebro.broker.set_cash(100000)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe_ratio')
cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')

results = cerebro.run()

print('Sharpe Ratio:', results[0].analyzers.sharpe_ratio.get_analysis())
print('Drawdown:', results[0].analyzers.drawdown.get_analysis())
print('Annual Return:', results[0].analyzers.annual_return.get_analysis())

cerebro.plot()
