import backtrader as bt

class EmergingMarketStrategy(bt.Strategy):
    def __init__(self):
        self.month_counter = 0
        self.rebalance_period = 6

    def next(self):
        # Check if it's time to rebalance the portfolio
        self.month_counter += 1
        if self.month_counter % self.rebalance_period != 0:
            return

        # Calculate 60-month performance
        past_60_month_perf = [d.close[0] / d.close[-60] for d in self.datas]

        # Calculate 6-month momentum
        six_month_momentum = [d.close[0] / d.close[-6] for d in self.datas]

        # Sort countries by 60-month performance and create late-stage groups
        sorted_indices = sorted(range(len(past_60_month_perf)), key=lambda k: past_60_month_perf[k])
        lw_group = sorted_indices[:len(self.datas) // 4]
        ll_group = sorted_indices[-len(self.datas) // 4:]

        # Rank countries in each subgroup by 6-month momentum
        lw_ranked = sorted(lw_group, key=lambda k: six_month_momentum[k], reverse=True)
        ll_ranked = sorted(ll_group, key=lambda k: six_month_momentum[k], reverse=True)

        # Set target positions
        for i, data in enumerate(self.datas):
            target_weight = 0

            # Set long positions for top 50% of best 6-month momentum in LL group
            if i in ll_ranked[:len(ll_group) // 2]:
                target_weight = 1 / (len(ll_group) // 2)

            # Set short positions for bottom 50% of worst 6-month momentum in LW group
            if i in lw_ranked[-len(lw_group) // 2:]:
                target_weight = -1 / (len(lw_group) // 2)

            # Rebalance the portfolio
            self.order_target_percent(data, target_weight)
