import backtrader as bt

class FilteredReversalStrategy(bt.Strategy):
    params = (
        ('n', 2),
        ('filter_percent', 0.2),
        ('lookback_period', 60),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.daily_returns = self.dataclose / self.dataclose(-1) - 1
        self.runs = 0

    def next(self):
        std_dev = bt.indicators.StdDev(self.daily_returns, period=self.p.lookback_period)
        filter_threshold = self.p.filter_percent * std_dev[0]
        
        if abs(self.daily_returns[0]) < filter_threshold:
            return
        
        if self.daily_returns[0] > 0:
            self.runs = self.runs + 1 if self.runs > 0 else 1
        else:
            self.runs = self.runs - 1 if self.runs < 0 else -1
        
        current_position = self.getposition().size
        
        if self.runs <= -self.p.n and current_position <= 0:
            self.order_target_percent(target=1)
        elif self.runs >= self.p.n and current_position >= 0:
            self.order_target_percent(target=-1)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    data = bt.feeds.YourSPXDataFeed(dataname='SPX')
    cerebro.adddata(data)
    cerebro.addstrategy(FilteredReversalStrategy)
    cerebro.run()
