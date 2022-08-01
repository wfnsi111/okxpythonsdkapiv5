# -*- coding: utf-8 -*-

import pandas as pd
import mplfinance as mpf
import time
import csv
import numpy as np
from basetrade.basetrade import BaseTrade
import re
import os

api_key = "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2"
secret_key = "A23C7CEB8046F39369CF73BDEBE985F5"
passphrase = "Kangkang1_"
# flag是实盘与模拟盘的切换参数
flag = '1'  # 模拟盘 demo trading
# flag = '0'  # 实盘 real trading


class MaAlarm(BaseTrade):
    def __init__(self, instId, ma, bar_lst, api_key=None, secret_key=None, passphrase=None, use_server_time=False):
        super().__init__(api_key, secret_key, passphrase)
        self.ma = ma
        self.bar_lst = bar_lst
        self.instId = instId
        self.df = None


    def drow_k(self, df, ma_list=None):
        ma_list = [self.ma]
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
        args_list = [mpf.make_addplot(df[ma_list])]
        args_list.append(mpf.make_addplot(df['signal_short'], scatter=True, markersize=80, marker="v", color='r'))
        # args_list.append(mpf.make_addplot(df['signal_long'], scatter=True, markersize=80, marker="v", color='r'))
        add_plot = args_list
        # 画K线
        mpf.plot(df, type='candle', addplot=add_plot, title=title, ylabel='prise(usdt)', style=my_style, volume=True, ylabel_lower='volume')
        # mpf.plot(df, type='candle', addplot=add_plot, title=title, ylabel='prise(usdt)', style=my_style)

    def get_history_data(self, bar):
        df = self._get_market_data(self.instId, bar)
        ma = int(re.findall(r"\d+", self.ma)[0])
        df[self.ma] = df['close'].rolling(ma).mean()
        return df

    def start_my_trade(self):
        start = 0
        while True:
            for index, bar in enumerate(self.bar_lst):
                #  获取K线数据
                df = self._get_candle_data(self.instId, bar)
                ma = int(re.findall(r"\d+", self.ma)[0])
                df[self.ma] = df['close'].rolling(ma).mean()

                check_flag = self.check_price_to_ma(df)
                if check_flag == 1:
                    start = 1
                    self.alarm_signal()
                    print("%s到均线%s附近" % (bar, self.ma))
                    break
                else:
                    pass
            if start == 1:
                break

            time.sleep(10)

    def check_price_to_ma(self, df):
        # 最新价格等于均线的时候 示警
        row = df.iloc[-1, :]
        ma = row[self.ma]
        high = row['high']
        low = row['low']
        if float(high) >= float(ma) and float(low) <= float(ma):
            return 1
        return 0

    def alarm_signal(self):
        abs_path = os.path.abspath(os.path.dirname(os.getcwd()))
        p = os.path.join(abs_path, 'mymusic', 'bpmtest.mp3')
        os.system(p)


if __name__ == '__main__':
    api_key = "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2"
    secret_key = "A23C7CEB8046F39369CF73BDEBE985F5"
    passphrase = "Kangkang1_"
    # flag是实盘与模拟盘的切换参数
    flag = '1'  # 模拟盘 demo trading
    # flag = '0'  # 实盘 real trading

    # instId = 'BTC-USDT-SWAP'
    instId = 'ETH-USDT-SWAP'
    ma = "MA60"
    bar1_list = ['5m', '1H', '2H', '4H']
    my_ma_trade = MaAlarm(instId, ma, bar1_list, api_key, secret_key, passphrase)
    my_ma_trade.start_my_trade()


