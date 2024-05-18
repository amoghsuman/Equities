import backtrader as bt
import numpy as np
import pandas as pd
import statsmodels.api as sm

class BigStocksAlpha(bt.Strategy):
    def __init__(self):
        self.rebalance_days = 0

    def next(self):
        if self.rebalance_days > 0:
            self.rebalance_days -= 1
            return

        if len(self.datas[0]) < 5 * 252:
            return

        alphas, betas, market_caps = [], [], []
        for data in self.datas:
            returns = pd.Series(data.get(size=5 * 252)).pct_change().dropna()
            market_returns = returns.iloc[:, 0]
            asset_returns = returns.iloc[:, 1]
            X = sm.add_constant(market_returns)
            Y = asset_returns
            model = sm.OLS(Y, X).fit()
            alpha, beta = model.params[0], model.params[1]
            market_cap = data.market_cap[0]
            alphas.append(alpha)
            betas.append(beta)
            market_caps.append(market_cap)

        alphas = np.array(alphas)
        betas = np.array(betas)
        market_caps = np.array(market_caps)
        big_stocks = market_caps > np.percentile(market_caps, 70)
        alphas_big = alphas[big_stocks]
        median_alpha = np.median(alphas_big)
        long_stocks = alphas_big < median_alpha
        short_stocks = alphas_big > median_alpha

        self.rebalance_days = 252
        self.order_target_percent(self.data0, 0.0)
        for data, alpha in zip(self.datas[big_stocks][long_stocks], alphas_big[long_stocks]):
            weight = (1 - np.argsort(np.argsort(alphas_big[long_stocks])) + 1) / np.sum(np.argsort(np.argsort(alphas_big[long_stocks])) + 1)
            self.order_target_percent(data, weight)

        for data, alpha in zip(self.datas[big_stocks][short_stocks], alphas_big[short_stocks]):
            weight = (np.argsort(np.argsort(alphas_big[short_stocks])) + 1) / np.sum(np.argsort(np.argsort(alphas_big[short_stocks])) + 1)
            self.order_target_percent(data, -weight)


cerebro = bt.Cerebro()
cerebro.broker.setcash(1000000.0)
cerebro.broker.setcommission(commission=0.001)

# Add data feeds here

cerebro.addstrategy(BigStocksAlpha)
cerebro.run()
