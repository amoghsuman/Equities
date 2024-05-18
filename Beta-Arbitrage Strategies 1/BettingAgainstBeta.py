import backtrader as bt
import pandas as pd
import numpy as np

class BettingAgainstBeta(bt.Strategy):
    params = (
        ('beta_window', 252),  # 1-year rolling window for beta calculation
        ('rebalance_freq', 20)  # Monthly rebalancing
    )

    def __init__(self):
        self.etfs = self.datas[1:]  # All country ETFs
        self.msci_index = self.datas[0]  # MSCI US Equity Index        self.counter = 0

    def next(self):
        self.counter += 1
        if self.counter % self.params.rebalance_freq == 0:
            etf_betas = []
            for etf in self.etfs:
                returns_etf = pd.Series(etf.get_array('close')[-self.params.beta_window:]).pct_change().dropna()
                returns_index = pd.Series(self.msci_index.get_array('close')[-self.params.beta_window:]).pct_change().dropna()
                beta = np.cov(returns_etf, returns_index)[0][1] / np.var(returns_index)
                etf_betas.append((etf, beta))
            etf_betas.sort(key=lambda x: x[1])  # Sort ETFs in ascending order by beta
            low_beta_etfs = etf_betas[:len(etf_betas) // 2]
            high_beta_etfs = etf_betas[len(etf_betas) // 2:]
            # Adjust positions - long on low-beta, short on high-beta
            for etf, beta in low_beta_etfs:
                self.order_target_percent(etf, target=1 / len(low_beta_etfs))
            for etf, beta in high_beta_etfs:
                self.order_target_percent(etf, target=-1 / len(high_beta_etfs))

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    # Load data for MSCI US Equity Index and Country ETFs
    # Assuming historical data is available as csv files
    msci_index_data = bt.feeds.YahooFinanceCSVData(dataname='path_to_msci_index_csv')
    etf_list = ['path_to_etf1_csv', 'path_to_etf2_csv', 'path_to_etf3_csv', ...]
    cerebro.adddata(msci_index_data)
    for etf_data_path in etf_list:
        etf_data = bt.feeds.YahooFinanceCSVData(dataname=etf_data_path)
        cerebro.adddata(etf_data)
    cerebro.addstrategy(BettingAgainstBeta)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)  # Set broker commission
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
