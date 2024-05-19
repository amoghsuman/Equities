import backtrader as bt

class AccrualAnomaly(bt.Strategy):
    def __init__(self):
        self.accruals = {}

    def next(self):
        if self.data.datetime.date().month != 5:  # Rebalance only in May
            return
        self.accruals.clear()
        for data in self.datas:
            ca = data.current_assets
            cash = data.cash_equivalents
            cl = data.current_liabilities
            std = data.short_term_debt
            itp = data.income_taxes_payable
            dep = data.depreciation_amortization_expense

            delta_ca = ca - ca(-1)
            delta_cash = cash - cash(-1)
            delta_cl = cl - cl(-1)
            delta_std = std - std(-1)
            delta_itp = itp - itp(-1)

            bs_acc = (delta_ca - delta_cash) - (delta_cl - delta_std - delta_itp) - dep
            self.accruals[data] = bs_acc

        sorted_stocks = sorted(self.datas, key=lambda d: self.accruals[d])

        low_decile = int(len(sorted_stocks) * 0.1)
        high_decile = int(len(sorted_stocks) * 0.9)

        long_stocks = sorted_stocks[:low_decile]
        short_stocks = sorted_stocks[high_decile:]

        self.sell_stocks(short_stocks)
        self.buy_stocks(long_stocks)

    def sell_stocks(self, short_stocks):
        for stock in short_stocks:
            self.sell(data=stock)

    def buy_stocks(self, long_stocks):
        for stock in long_stocks:
            self.buy(data=stock)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(AccrualAnomaly)
    # Add your data feeds for NYSE, AMEX, and NASDAQ stocks here
    cerebro.run()
