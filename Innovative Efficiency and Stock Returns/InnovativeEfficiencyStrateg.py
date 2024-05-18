import backtrader as bt

class InnovativeEfficiencyStrategy(bt.Strategy):
    def __init__(self):
        self.rnd_exp = dict()

    def prenext(self):
        self.next()

    def next(self):
        if len(self.datas) < 2:
            return
        if self.datetime.date(ago=-12).month == self.datetime.date().month:
            self.rebalance_portfolio()

    def rebalance_portfolio(self):
        stocks_with_patents = []
        for data in self.datas:
            if data._name not in self.rnd_exp:
                continue
            if data.patents > 0:
                stocks_with_patents.append(data)
        if not stocks_with_patents:
            return
        stocks_with_patents.sort(key=lambda data: data.patents / self.rnd_exp[data._name][-2], reverse=True)
        third = len(stocks_with_patents) // 3
        long_stocks = stocks_with_patents[:third]
        short_stocks = stocks_with_patents[-third:]
        for data in long_stocks:
            self.order_target_percent(data, target=1.0 / len(long_stocks))
        for data in short_stocks:
            self.order_target_percent(data, target=-1.0 / len(short_stocks))
        for data in self.datas:
            if data not in long_stocks + short_stocks:
                self.order_target_percent(data, target=0.0)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED, {order.executed.price}")
            elif order.issell():
                self.log(f"SELL EXECUTED, {order.executed.price}")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

    def log(self, txt, dt=None):
        dt = dt or self.datetime.date()
        print(f"{dt.isoformat()}, {txt}")

def run_strategy():
    cerebro = bt.Cerebro()
    # Load data and filter stocks
    # Add your own data loading and filtering code here
    # Add the strategy to the cerebro instance
    cerebro.addstrategy(InnovativeEfficiencyStrategy)
    # Set the starting cash
    cerebro.broker.setcash(100000.0)
    # Run the backtest
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    cerebro.run()
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

if __name__ == "__main__":
    run_strategy()
