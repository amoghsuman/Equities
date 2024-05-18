import backtrader as bt
import backtrader.feeds as btfeeds
import pandas as pd

class SalesSeasonality(bt.Strategy):
    def __init__(self):
        self.sea = {}
        self.avgsea = {}

    def prenext(self):
        self.next()

    def next(self):
        for data in self.datas:
            symbol = data._name
            if symbol not in self.sea:
                self.sea[symbol] = []
            if symbol not in self.avgsea:
                self.avgsea[symbol] = []
            
            sales = data.sales[0]
            annual_sales = data.annualsales[0]
            sea = sales / annual_sales
            self.sea[symbol].append(sea)
            
            if len(self.sea[symbol]) >= 8:
                avgsea = sum(self.sea[symbol][-8:-4]) / 4
                self.avgsea[symbol].append(avgsea)

        if len(self.avgsea) > 0:
            sorted_symbols = sorted(self.avgsea, key=lambda x: self.avgsea[x][-1], reverse=True)
            long_symbols = sorted_symbols[:len(sorted_symbols)//10]
            short_symbols = sorted_symbols[-len(sorted_symbols)//10:]
            
            for data in self.datas:
                symbol = data._name
                if symbol in long_symbols:
                    self.order_target_percent(data, target=1 / len(long_symbols))
                elif symbol in short_symbols:
                    self.order_target_percent(data, target=-1 / len(short_symbols))
                else:
                    self.order_target_percent(data, target=0.0)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SalesSeasonality)
    
    # Load your data feed here
    # data = btfeeds.PandasData(dataname=your_dataframe)
    # cerebro.adddata(data)
    
    cerebro.broker.set_cash(100000)
    cerebro.run()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue()}")
