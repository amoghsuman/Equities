import backtrader as bt
import datetime

class MarketCapStrategy(bt.Strategy):
    params = (
        ('quintile', 5),
        ('rebalance_days', 252),
    )

    def __init__(self):
        self.counter = 0

    def next(self):
        self.counter += 1
        if self.counter % self.params.rebalance_days == 0:
            self.rebalance_portfolio()

    def rebalance_portfolio(self):
        market_caps = []
        for data in self.datas:
            market_cap = data.close[0] * data.volume[0]
            market_caps.append((data, market_cap))
        
        sorted_data = sorted(market_caps, key=lambda x: x[1])
        quintile_size = len(sorted_data) // self.params.quintile
        lowest_quintile = sorted_data[:quintile_size]
        
        # Calculate total market cap for lowest quintile
        total_market_cap = sum([x[1] for x in lowest_quintile])
        
        # Sell all current holdings
        for data in self.datas:
            self.order_target_percent(data, target=0)
        
        # Buy stocks in lowest quintile
        for data, market_cap in lowest_quintile:
            target_weight = market_cap / total_market_cap
            self.order_target_percent(data, target=target_weight)


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    
    # Add investment universe
    for ticker in ['NYSE_ticker1', 'NYSE_ticker2', 'AMEX_ticker1', 'NASDAQ_ticker1']:
        data = bt.feeds.YahooFinanceData(
            dataname=ticker,
            fromdate=datetime.datetime(2015, 1, 1),
            todate=datetime.datetime(2021, 9, 30),
            adjclose=True,
            plot=False,
        )
        cerebro.adddata(data)
    
    cerebro.addstrategy(MarketCapStrategy)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
