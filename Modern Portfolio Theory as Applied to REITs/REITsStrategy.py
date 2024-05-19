import backtrader as bt
import pandas as pd

class REITsStrategy(bt.Strategy):
    def __init__(self):
        # Define universe
        self.universe = pd.read_csv('nyse_amex_nasdaq.csv')['Symbol'].tolist()
        # Quarter percentiles to exclude
        self.bm_exclusion_percentiles = (0.005, 0.995)
        # Time parameters
        self.year_start = self.datas[0].datetime.date(0).year
        self.rebalance_year = self.year
        # Set length of holding period
        self.holding_period = 252  # trading days in a year
        # Keep track of cheap and expensive REITs
        self.expensive_reits = []
        self.cheap_reits = []

    def start_year(self):
        # Update current year
        self.year = self.datas[0].datetime.date(0).year
        # Update list of investment universe
        self.universe = pd.read_csv('nyse_amex_nasdaq.csv')['Symbol'].tolist()
        # Get fundamental data from Yahoo Finance
        self.bm_ratio = self.get_bm_ratio()
        # Exclude extreme B/M values
        self.exclude_extreme_bms()
        # Rank the remaining REITs based on their B/M ratio
        self.rank_reits()
        # Assign REITs to expensive and cheap portfolios
        self.assign_portfolios()
        # Calculate weights for each REIT in the portfolio
        self.calculate_weights()
        # Go long on cheap REITs
        for data in self.cheap_reits:
            self.order_target_percent(data, target=self.weights[data])

    def next(self):
        # Skip if not at the end of the year
        if self.datas[0].datetime.date(0).year == self.rebalance_year:
            return
        # Set the new rebalancing year
        self.rebalance_year = self.datas[0].datetime.date(0).year
        # Close all existing positions
        self.close()
        # Assign REITs to expensive and cheap portfolios
        self.assign_portfolios()
        # Calculate weights for each REIT in the portfolio
        self.calculate_weights()
        # Go long on cheap REITs
        for data in self.cheap_reits:
            self.order_target_percent(data, target=self.weights[data])

    def get_bm_ratio(self):
        bm_ratio = {}
        for sym in self.universe:
            data = bt.feeds.YahooFinanceData(
                dataname=sym,
                fromdate=datetime(self.year, 1, 1),
                todate=datetime(self.year, 12, 31),
                buffered=True,
                reverse=False
            )
            df = data.to_pandas()
            bm_ratio[sym] = df['Book Value'][0] / df['Market Capitalization'][0]
        return bm_ratio

    def exclude_extreme_bms(self):
        sorted_bms = sorted(self.bm_ratio.items(), key=lambda x: x[1])
        num_excluded = int(len(sorted_bms) * 0.005)
        self.universe = [x[0] for x in sorted_bms[num_excluded:len(sorted_bms) - num_excluded]]

    def rank_reits(self):
        sorted_bms = sorted(self.bm_ratio.items(), key=lambda x: x[1], reverse=True)
        self.sorted_reits = [x[0] for x in sorted_bms]
        return self.sorted_reits

    def assign_portfolios(self):
        bm1_num = int(len(self.sorted_reits) * 0.2)
        bm5_num = int(len(self.sorted_reits) * 0.8)
        self.expensive_reits = self.sorted_reits[len(self.sorted_reits) - bm1_num:]
        self.cheap_reits = self.sorted_reits[:bm5_num]

    def calculate_weights(self):
        num_expensive = len(self.expensive_reits)
        num_cheap = len(self.cheap_reits)
        # Calculate equal weights
        weight_expensive = 1 / num_expensive
        weight_cheap = 1 / num_cheap
        # Assign weights to each REIT in the portfolio
        self.weights = {}
        for data in self.expensive_reits:
            self.weights[data] = weight_expensive
        for data in self.cheap_reits:
            self.weights[data] = weight_cheap
