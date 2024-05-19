import backtrader as bt

class DiversityStrategy(bt.Strategy):
    def __init__(self):
        self.diversity = self.datas[0].diversity

    def next(self):
        long_positions = []
        short_positions = []

        for data in self.datas:
            if len(data) < 12 or data.book_value[0] <= 0:
                continue
            if data.diversity[0] >= data.diversity.get(size=5)[0]:
                long_positions.append(data)
            elif data.diversity[0] <= data.diversity.get(size=5)[-1]:
                short_positions.append(data)

        long_weight = 1.0 / len(long_positions)
        short_weight = -1.0 / len(short_positions)

        for data in long_positions:
            self.order_target_percent(data=data, target=long_weight)
        for data in short_positions:
            self.order_target_percent(data=data, target=short_weight)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(DiversityStrategy)

    # Add data feeds from NYSE, AMEX, NASDAQ with biographical data from EDGAR (not shown)
    # Use the provided diversity measure as an additional data field (not shown)
    
    cerebro.run()
