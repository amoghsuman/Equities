import backtrader as bt
import pandas as pd
import numpy as np

class IndustryMomentumReversal(bt.Strategy):
    params = (
        ('lookback_long', 120),
        ('lookback_short', 12),
        ('holding_period', 3),
    )

    def __init__(self):
        self.month_counter = 0

    def next(self):
        self.month_counter += 1
        if self.month_counter % self.params.holding_period != 0:
            return

        performance_long = {}
        performance_short = {}

        for d in self.getdatanames():
            data = self.getdatabyname(d)
            if len(data) < self.params.lookback_long:
                continue

            performance_long[d] = (data.close[0] / data.close[-self.params.lookback_long]) - 1
            performance_short[d] = (data.close[0] / data.close[-self.params.lookback_short]) - 1

        sorted_by_long = sorted(performance_long.items(), key=lambda x: x[1])
        losers = sorted_by_long[:len(sorted_by_long) // 4]
        winners = sorted_by_long[-len(sorted_by_long) // 4:]

        losers_sorted_by_short = sorted(losers, key=lambda x: x[1], reverse=True)
        winners_sorted_by_short = sorted(winners, key=lambda x: x[1])

        selected_losers = [x[0] for x in losers_sorted_by_short[:len(losers_sorted_by_short) // 4]]
        selected_winners = [x[0] for x in winners_sorted_by_short[:len(winners_sorted_by_short) // 4]]

        positions = self.broker.get_value()

        for d in self.getdatanames():
            data = self.getdatabyname(d)
            position_size = positions / (len(selected_losers) + len(selected_winners))

            if d in selected_losers:
                self.order_target_value(data, target=position_size)
            elif d in selected_winners:
                self.order_target_value(data, target=-position_size)
            else:
                self.order_target_value(data, target=0)

cerebro = bt.Cerebro()

# Add data feeds here with appropriate names
# Example:
# data = bt.feeds.YahooFinanceData(dataname='SPY', fromdate=start_date, todate=end_date)
# cerebro.adddata(data, name='SPY')

cerebro.addstrategy(IndustryMomentumReversal)
cerebro.broker.setcash(1000000)
cerebro.broker.setcommission(commission=0.001)

print('Starting Portfolio Value:', cerebro.broker.getvalue())
cerebro.run()
print('Final Portfolio Value:', cerebro.broker.getvalue())
