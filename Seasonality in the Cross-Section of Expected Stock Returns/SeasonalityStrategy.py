import backtrader as bt
import numpy as np

class SeasonalityStrategy(bt.Strategy):
    params = (
        ('top_percent', 0.3),
        ('num_portfolios', 10),
        ('lookback_period', 12),
        ('rebalance_days', 21)
    )

    def __init__(self):
        self.add_timer(bt.timer.SESSION_END, monthdays=[1], monthcarry=True)
        self.inds = {}
        for d in self.datas:
            self.inds[d] = {}
            self.inds[d]['market_cap'] = d.close * d.volume
            self.inds[d]['past_performance'] = bt.ind.PctChange(d.close, period=self.p.lookback_period)

    def notify_timer(self, timer, when, *args, **kwargs):
        if self._last_month != self.data.datetime.date(0).month:
            self._last_month = self.data.datetime.date(0).month
            self.rebalance_portfolio()

    def rebalance_portfolio(self):
        market_caps = [self.inds[d]['market_cap'][0] for d in self.datas]
        past_performances = [self.inds[d]['past_performance'][0] for d in self.datas]
        sorted_indices = np.argsort(market_caps)[::-1]
        top_percentile = int(len(sorted_indices) * self.p.top_percent)
        top_firms = sorted_indices[:top_percentile]
        selected_stocks = [self.datas[i] for i in top_firms]
        selected_performances = [past_performances[i] for i in top_firms]
        sorted_stocks = np.argsort(selected_performances)
        num_in_decile = int(len(sorted_stocks) / self.p.num_portfolios)
        long_decile = sorted_stocks[-num_in_decile:]
        short_decile = sorted_stocks[:num_in_decile]
        long_stocks = [selected_stocks[i] for i in long_decile]
        short_stocks = [selected_stocks[i] for i in short_decile]
        for d in self.datas:
            current_position = self.getposition(d).size
            if d in long_stocks and current_position <= 0:
                self.order_target_percent(d, target=1.0 / len(long_stocks))
            elif d in short_stocks and current_position >= 0:
                self.order_target_percent(d, target=-1.0 / len(short_stocks))
            elif current_position != 0:
                self.close(d)cerebro = bt.Cerebro()
# Add data feeds, broker, etc.
cerebro.addstrategy(SeasonalityStrategy)
results = cerebro.run()
