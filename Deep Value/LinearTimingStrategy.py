import backtrader as bt
from scipy.stats import zscore

class LinearTimingStrategy(bt.Strategy):
    def __init__(self):
        self.inds = {}
        self.stocks = []
        total_market_cap = 0  # total market capitalization in the CRSP file

        # get the largest stocks whose market capitalizations cumulate to 75% of total market capitalization
        self.stocks = [s for s in self.datas if s.market_cap > 0]
        self.stocks.sort(key=lambda s: s.market_cap, reverse=True)
        for s in self.stocks:
            total_market_cap += s.market_cap
            if total_market_cap >= 0.75 * total_market_cap:
                break

        # use industry-adjusted book-to-market ratios to measure the value of each firm
        for s in self.stocks:
            bm = s.book_value / s.market_cap
            bm_ind_adj = bm / s.industry_bm
            self.inds[s] = {'bm_ind_adj': bm_ind_adj}
        
        self.add_timer(monthdays=[1,])  # rebalance monthly on first day of each month

    def next(self):
        # get the value signal of each stock
        value_signals = [self.inds[s]['bm_ind_adj'] for s in self.stocks]
        # form value-weighted decile portfolios each month by sorting on BM i,t,Ind.adj.
        deciles = {}
        for i in range(1, 11):
            decile_size = len(self.stocks) // 10
            decile = sorted(self.stocks, key=lambda s: self.inds[s]['bm_ind_adj'])[i*decile_size:(i+1)*decile_size]
            deciles[i] = decile
        # define the value and growth portfolios
        value_portfolio = deciles[10]
        growth_portfolio = deciles[1]
        # calculate value spread as the difference between the average value signal in the high and low portfolio
        value_spread = sum(self.inds[s]['bm_ind_adj'] for s in value_portfolio) / len(value_portfolio) - \
                       sum(self.inds[s]['bm_ind_adj'] for s in growth_portfolio) / len(growth_portfolio)
        # standardize the value spread using historical information
        value_spreads = [value_spread]
        for i in range(1, 12):
            prev_month_start = self.datetime.date().replace(month=self.datetime.date().month-i, day=1)
            prev_month_end = prev_month_start.replace(day=bt.num2date(bt.date2num(prev_month_start)).daysinmonth)
            prev_month_spread = (sum(self.inds[s]['bm_ind_adj'][prev_month_start:prev_month_end] for s in value_portfolio) / 
                                 len(value_portfolio)) - \
                                (sum(self.inds[s]['bm_ind_adj'][prev_month_start:prev_month_end] for s in growth_portfolio) / 
                                 len(growth_portfolio))
            value_spreads.append(prev_month_spread)
        std_signal = zscore(value_spreads)[-1]  # the standardized signal of the most recent month
        # cut off the standardized signal at ±2
        std_signal = max(-2, min(2, std_signal))
        # invest VSt,His dollars long or short accordingly to the signal and rebalance monthly
        for s in self.stocks:
            if self.inds[s]['bm_ind_adj'] > std_signal:
                self.order_target_percent(s, target=0.1)
            elif self.inds[s]['bm_ind_adj'] < std_signal:
                self.order_target_percent(s, target=-0.1)
            else:
                self.order_target_percent(s, target=0)  # do not hold the stock
