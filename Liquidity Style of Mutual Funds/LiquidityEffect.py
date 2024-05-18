import backtrader as bt
import pandas as pd

class LiquidityEffect(bt.Strategy):
    def __init__(self):
        self.small_cap_funds = self.get_small_cap_funds()

    def next(self):
        if self.datetime.date().month == 1 and self.datetime.date().day == 1:
            self.rebalance_portfolio()

    def get_small_cap_funds(self):
        # Retrieve small-cap equity mutual funds list from a data source
        pass

    def calculate_liquidity_score(self, fund):
        holdings = self.get_fund_holdings(fund)
        liquidity_scores = []
        for stock in holdings:
            turnover = stock["shares_traded"] / stock["outstanding_shares"]
            liquidity_scores.append(turnover * stock["weight"])
        return sum(liquidity_scores)

    def get_fund_holdings(self, fund):
        # Retrieve end-of-year equity holdings for the given fund from a data source
        pass

    def rebalance_portfolio(self):
        liquidity_scores = {}
        for fund in self.small_cap_funds:
            liquidity_scores[fund] = self.calculate_liquidity_score(fund)
        sorted_funds = sorted(liquidity_scores, key=liquidity_scores.get)
        top_quintile = sorted_funds[:len(sorted_funds) // 5]
        for fund in self.small_cap_funds:
            if fund in top_quintile:
                self.order_target_percent(fund, target=1 / len(top_quintile))
            else:
                self.order_target_percent(fund, target=0)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(LiquidityEffect)
    # Add small-cap equity mutual funds data to Cerebro
    # ...
    cerebro.run()
