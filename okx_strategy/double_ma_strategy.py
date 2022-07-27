"""
5分钟K线， 双均线策略
MA1: 5
MA2: 10

"""

import pandas as pd
import mplfinance as mpf
import time
import csv
import numpy as np
import okx.Market_api as Market
# from pandas.core.frame import DataFrame
from basetrade.basetrade import BaseTrade
import re


class Double_Ma_Strategy(BaseTrade):
    def __init__(self, instId, ma1, ma2, bar, api_key=None, secret_key=None, passphrase=None, use_server_time=False):
        super().__init__(api_key, secret_key, passphrase)

        self.instId = instId
        self.bar = bar
        self.ma1 = ma1
        self.ma2 = ma2
        self.df_market_data = None
        self.df_3mins = None
        self.has_order = False

    def drow_k(self, df, ma_list=None):
        df = df.apply(pd.to_numeric, errors='ignore')
        title = 'MY_test'
        # 设置颜色, edge的意思是设置K线边框的颜色，默认是黑色，
        # edge=’inherit’的意思是保持K线边框的颜色与K线实体颜色一致,
        # volume=’inherit’意思是将成交量柱状图的颜色设置为红涨绿跌，与K线一致。wick 引线
        my_color = mpf.make_marketcolors(up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
        my_style = mpf.make_mpf_style(marketcolors=my_color)
        # 添加均线指标
        # 添加买卖点
        # marker参数用来设定交易信号图标的形状，marker=’^’表示向上的箭头， marker=’v’表示向下的箭头， marker=’o’表示圆圈。
        # color参数可以用来控制颜色，color=’g’表示绿色（green）, ‘y’表示黄色（yellow）， ‘b’表示蓝色（blue），可以根据自己的偏好设定不同的颜色。
        # add_plot = [mpf.make_addplot(df[ma_list])]
        # add_plot.append(mpf.make_addplot(df['signal_short'], scatter=True, markersize=80, marker="v", color='r'))
        # add_plot.append(mpf.make_addplot(df['signal_long'], scatter=True, markersize=80, marker="v", color='r'))
        # 画K线
        # mpf.plot(df, type='candle', addplot=add_plot, title=title, ylabel='prise(usdt)', style=my_style, volume=True, ylabel_lower='volume')

        # 使用mpf.figure()函数可以返回一个figure对象，从而进入External Axes Mode，从而实现对Axes对象和figure对象的自由控制
        fig = mpf.figure(style=my_style, figsize=(12, 8), facecolor=(0.82, 0.83, 0.85))
        # 添加2个图表，四个数字分别代表图表左下角在figure中的坐标，以及图表的宽（0.88）、高（0.60）
        ax1 = fig.add_axes([0.06, 0.25, 0.88, 0.60])
        # 添加第二图表时，使用sharex关键字指明与ax1在x轴上对齐，且共用x轴
        ax2 = fig.add_axes([0.06, 0.15, 0.88, 0.10], sharex=ax1)
        # 设置2张图表的Y轴标签
        ax1.set_ylabel('price')
        ax2.set_ylabel('volume')
        # 添加均线
        add_plot = [mpf.make_addplot(df[ma_list], ax=ax1)]
        # 添加买卖点
        add_plot.append(mpf.make_addplot(df['drow_short'], scatter=True, markersize=40, marker="v", color='black', ax=ax1))
        add_plot.append(mpf.make_addplot(df['drow_long'], scatter=True, markersize=40, marker="^", color='b', ax=ax1))
        # add_plot.append(mpf.make_addplot(df['order'].values, type='scatter', markersize=20, marker='v', color='g', ax=ax1))
        # 调用mpf.plot()函数，注意调用的方式跟上一节不同，这里需要指定ax=ax1，volume=ax2，将K线图显示在ax1中，交易量显示在ax2中
        mpf.plot(df, ax=ax1, volume=ax2, type='candle', style=my_style, addplot=add_plot)
        fig.show()


    def start_my_trade(self):
        while True:
            self.get_market_data()
            # # 根据交易信号的变化下单，当交易信号从0变为1的时候买入， 1变为0卖出 交易信号不变的时候 不下单
            self.market_open()
            print("wait 60s  ")
            time.sleep(60)

    def market_open(self):
        last_row = self.df_market_data.iloc[-1, :]
        order = last_row['order']
        self.has_order = self.get_positions()
        if order == 1:
        # if True:
            # 如果有仓位 平仓之后 开多
            if self.has_order:
                # result = self.tradeAPI.close_positions(self.instId, self.tdMode, posSide='long',  ccy="USDT")
                result = self.close_positions_all()
                self.has_order = False
            para = {
                "instId": self.instId,
                "tdMode": self.tdMode,
                "ccy": 'USDT',
                'side': 'buy',
                'ordType': 'market',
                'sz': self.sz,
                'px': '',
                'posSide': 'long'

            }
            result = self.tradeAPI.place_order(**para)
            ordId, sCode, sMsg = self.check_order_result_data(result, 'ordId')
            if sCode == "0":
                self.has_order = True
        elif order == -1:
            # 做空
            if self.has_order:
                result = self.close_positions_all()
                self.has_order = False
            para = {
                "instId": self.instId,
                "tdMode": self.tdMode,
                "ccy": 'USDT',
                'side': 'sell',
                'ordType': 'market',
                'sz': self.sz,
                'px': '',
                'posSide': 'short'

            }
            result = self.tradeAPI.place_order(**para)
            ordId, sCode, sMsg = self.check_order_result_data(result, 'ordId')
            if sCode == "0":
                self.has_order = True
        else:
            pass

    def get_market_data(self):
        """ 获取历史K线数据 """

        self.df_market_data = self._get_market_data(self.instId, self.bar)
        ma1 = int(re.findall(r"\d+", self.ma1)[0])
        ma2 = int(re.findall(r"\d+", self.ma2)[0])
        self.df_market_data[self.ma1] = self.df_market_data['close'].rolling(ma1).mean()
        self.df_market_data[self.ma2] = self.df_market_data['close'].rolling(ma2).mean()
        # MA5大于MA10标记为1，反之为0
        self.df_market_data["signal"] = np.where(self.df_market_data[self.ma1] > self.df_market_data[self.ma2], 1, 0)
        # 根据交易信号的变化下单，当交易信号从0变为1的时候买入， 1变为0卖出 交易信号不变的时候 不下单
        self.df_market_data['order'] = self.df_market_data['signal'].diff()

        self.df_market_data["drow_long"] = np.where(self.df_market_data['order'] == 1, self.df_market_data['low'], None)
        self.df_market_data["drow_short"] = np.where(self.df_market_data['order'] == -1, self.df_market_data['high'], None)
        # self.drow_k(self.df_market_data, [self.ma1, self.ma2])
        # return self.df_market_data


if __name__ == '__main__':
    api_key = "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2"
    secret_key = "A23C7CEB8046F39369CF73BDEBE985F5"
    passphrase = "Kangkang1_"
    ma1 = "MA5"
    ma2 = "MA10"
    bar = '1m'
    instId = 'ETH-USDT-SWAP'
    my_ma_trade = Double_Ma_Strategy(instId, ma1, ma2, bar, api_key, secret_key, passphrase)
    my_ma_trade.start_my_trade()


