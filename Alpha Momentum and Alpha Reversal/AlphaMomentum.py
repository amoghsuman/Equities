import backtrader as bt

class AlphaMomentum(bt.Strategy):
    params = (
        ('lookback', 12),
    )

    def __init__(self):
        self.alphas = {}
        self.market_rets = {}
        self.scores = {}

    def next(self):
        # Compute alphas and returns for each index
        for d in self.getdatanames():
            data = self.getdatabyname(d)
            # Compute returns and alphas using simple CAPM model
            market_ret = data.close[0] / data.close[-1] - 1
            self.market_rets[d] = market_ret
            alpha = market_ret - (self._owner.broker.getvalue() / self._owner.broker.startingcash - 1)
            self.alphas[d] = alpha
            # Calculate alpha score
            alpha_vol = bt.indicators.StdDev(self.alphas[d], period=self.params.lookback)
            self.scores[d] = alpha / alpha_vol

        # Determine alpha momentum and rank indexes
        sorted_indexes = sorted(self.scores, key=self.scores.get, reverse=True)
        top_quintile = sorted_indexes[:len(sorted_indexes) // 5]
        bottom_quintile = sorted_indexes[-(len(sorted_indexes) // 5):]

        # Positioning: Long highest quintile, short lowest quintile
        for d in self.getdatanames():
            data = self.getdatabyname(d)
            position_size = self.broker.getvalue() / (len(top_quintile) + len(bottom_quintile))
            if d in top_quintile:
                self.order_target_value(data, target=position_size)
            elif d in bottom_quintile:
                self.order_target_value(data, target=-position_size)
            else:
                self.order_target_value(data, target=0)

        # Rebalance monthly
        self.notify_timer(when=bt.Timer.SESSION_END)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    
    # Add investment universe
    for index in range(51):
        data = bt.feeds.GenericCSVData(dataname=f'index_{index}.csv')
        cerebro.adddata(data, name=f'index_{index}')

    # Add strategy
    cerebro.addstrategy(AlphaMomentum)
    
    # Set initial cash and run backtest
    cerebro.broker.set_cash(100000)
    cerebro.run()
