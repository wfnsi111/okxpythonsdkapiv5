
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import csv
import numpy as np


class InterCandle:  # 定义一个交互K线图类
    def __init__(self, data, my_style):
        # 初始化交互式K线图对象，历史数据作为唯一的参数用于初始化对象
        self.data = data
        self.style = my_style
        # 设置初始化的K线图显示区间起点为0，即显示第0到第99个交易日的数据（前100个数据）
        self.idx_start = 0

        # 初始化figure对象，在figure上建立三个Axes对象并分别设置好它们的位置和基本属性
        self.fig = mpf.figure(style=my_style, figsize=(12, 8), facecolor=(0.82, 0.83, 0.85))
        fig = self.fig
        self.ax1 = fig.add_axes([0.08, 0.25, 0.88, 0.60])
        self.ax2 = fig.add_axes([0.08, 0.15, 0.88, 0.10], sharex=self.ax1)
        self.ax2.set_ylabel('volume')
        # 初始化figure对象，在figure上预先放置文本并设置格式，文本内容根据需要显示的数据实时更新
        # 初始化时，所有的价格数据都显示为空字符串

    def refresh_plot(self, idx_start=0):
        """ 根据最新的参数，重新绘制整个图表
        """
        plot_data = self.data
        # plot_data = all_data.iloc[idx_start: idx_start + 100]

        ap = []
        # 添加K线图重叠均线
        ap.append(mpf.make_addplot(plot_data[['MA5', 'MA10']], ax=self.ax1))
        # 绘制图表
        mpf.plot(plot_data,
                 ax=self.ax1,
                 volume=self.ax2,
                 addplot=ap,
                 type='candle',
                 style=self.style,
                 datetime_format='%Y-%m',
                 xrotation=0)
        self.fig.show()

    def refresh_texts(self, display_data):
        """ 更新K线图上的价格文本
        """
        # display_data是一个交易日内的所有数据，将这些数据分别填入figure对象上的文本中
        self.t3.set_text(f'{np.round(display_data["open"], 3)} / {np.round(display_data["close"], 3)}')
        self.t4.set_text(f'{display_data["change"]}')
        self.t5.set_text(f'[{np.round(display_data["pct_change"], 2)}%]')
        self.t6.set_text(f'{display_data.name.date()}')
        self.t8.set_text(f'{display_data["high"]}')
        self.t10.set_text(f'{display_data["low"]}')
        self.t12.set_text(f'{np.round(display_data["volume"] / 10000, 3)}')
        self.t14.set_text(f'{display_data["value"]}')
        self.t16.set_text(f'{display_data["upper_lim"]}')
        self.t18.set_text(f'{display_data["lower_lim"]}')
        self.t20.set_text(f'{np.round(display_data["average"], 3)}')
        self.t22.set_text(f'{display_data["last_close"]}')
        # 根据本交易日的价格变动值确定开盘价、收盘价的显示颜色
        if display_data['change'] > 0:  # 如果今日变动额大于0，即今天价格高于昨天，今天价格显示为红色
            close_number_color = 'red'
        elif display_data['change'] < 0:  # 如果今日变动额小于0，即今天价格低于昨天，今天价格显示为绿色
            close_number_color = 'green'
        else:
            close_number_color = 'black'
        self.t1.set_color(close_number_color)
        self.t2.set_color(close_number_color)
        self.t3.set_color(close_number_color)


my_color = mpf.make_marketcolors(up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
my_style = mpf.make_mpf_style(marketcolors=my_color)
df = pd.read_csv('MYhistoryMA.csv', sep=',', parse_dates=['time'])
df.set_index(['time'], inplace=True)
# 创建一个InterCandle对象，显示风格为前面定义好的my_style风格（即中国股市惯例风格）
candle = InterCandle(df, my_style)
# 更新图表上的文本，显示第100个交易日的K线数据
# candle.refresh_texts(df)
# 更新显示第100天开始的K线图
candle.refresh_plot()
