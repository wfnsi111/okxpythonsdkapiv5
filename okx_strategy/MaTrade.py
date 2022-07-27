# -*- coding: utf-8 -*-

import pandas as pd
import mplfinance as mpf
import time
import csv
import numpy as np
# from pandas.core.frame import DataFrame
from basetrade.basetrade import BaseTrade
import re
from threading import Timer

api_key = "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2"
secret_key = "A23C7CEB8046F39369CF73BDEBE985F5"
passphrase = "Kangkang1_"
# flag是实盘与模拟盘的切换参数
flag = '1'  # 模拟盘 demo trading
# flag = '0'  # 实盘 real trading

# df['gtime']=pd.to_datetime(df['gtime'],unit='s'))


class MaTrade(BaseTrade):
    def __init__(self, instId, ma, bar, api_key=None, secret_key=None, passphrase=None, use_server_time=False):
        super().__init__(api_key, secret_key, passphrase)
        self.ma = ma
        self.df = None
        self.df_3mins = None
        self.bar1, self.bar2 = bar
        self.instId = instId

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

    def start_my_trade(self):
        self.has_order = self.get_positions()
        while True:
            time.sleep(10)
            # time.sleep(60)
            # 检测持仓
            # self.has_order = self.get_positions()
            if self.has_order:
                self.has_order = self.stop_order()
                if self.has_order:
                    continue

            if self.order_times == 3:
                break

            # 判断信号1
            signal1 = self.check_signal1()
            if not signal1:
                # pass
                self.log.info('%s震荡中....................' % self.bar2)
                continue

            self.log.info('%s行情处于趋势之中' % self.bar2)
            print('%s行情处于趋势之中' % self.bar2)

            # 判断信号2
            signal2 = self.check_signal2()
            if signal2:
                self.log.info('价格接近均线 %1 附近')
                signal_order_para = self.check_signal3(signal1)
                # signal_order_para = {"side": "buy", "posSide": "long"}
                # signal_order_para = {"side": "sell", "posSide": "short"}
                if signal_order_para:
                    self.log.info('3分钟满足开仓条件，准备开仓')
                    # 设置头寸
                    atr = self.get_atr_data()
                    self.sz = int(0.05 * self.mybalance / atr * 100)
                    self.posSide = signal_order_para.get('posSide')
                    self.side = signal_order_para.get('side')
                    # 开仓
                    self.ready_order(self.posSide, self.side, self.sz)



    def cal_profit(self, df):
        pass

    def trend_analyze(self, c_length=10):
        '''
        第一步： 判断趋势
            10根K线连续处于均线以下
        '''
        self.get_history_1h()
        up_count = 0
        down_count = 0
        for index, row in self.df.iterrows():
            # 多头判断
            if not row[self.ma]:
                continue
            if float(row['low']) > float(row[self.ma]) and row[self.ma]:
                up_count += 1
            else:
                up_count = 0

            if up_count >= c_length:
                # 多头趋势
                self.df.loc[index, 'signal_long'] = row['low']
                self.df.loc[index, 'signal_flag'] = 'long'
                # return 'bull'
            # 空头判断
            if float(row['high']) < float(row[self.ma]) and row[self.ma]:
                down_count += 1
            else:
                down_count = 0

            if down_count >= c_length:
                # 空头趋势
                self.df.loc[index, 'signal_short'] = row['high']
                self.df.loc[index, 'signal_flag'] = 'short'
                # return 'fall'
        # df.to_csv("test_MA_data.csv")

    def set_signal_1h(self):
        # 判断趋势
        try:
            data = self.df.iloc[-1, :]
            if data['signal_flag'] == 'long':
                trend_signal = 'long'
            elif data['signal_flag'] == 'short':
                trend_signal = 'short'
            else:
                trend_signal = False
            return trend_signal
        except Exception as e:
            # self.log.error('MA error......%s' % e)
            return False

    def get_long_signal_3min_confirm(self):
        """
        开多条件：
            1 下引线 大于实体
            2 vol是前K线的2倍
        """

        # df_3mins = self.get_3_min_data()
        # df_3mins = self.get_3min_data_history()
        df_3mins = self._get_market_data(self.instId, self.bar1, limit='2')

        front_volume = df_3mins.iloc[0, :]['volume']
        row2 = df_3mins.iloc[-1, :]
        condition = 0
        _volume = float(row2['volume'])
        _close = float(row2['close'])
        _open = float(row2['open'])
        _low = float(row2['low'])
        entity = abs(_close - _open)
        down_wick = min(_close, _open) - _low
        # 引线大于实体，
        if down_wick > entity:
            condition += 1

        # vol是前K线的2倍
        if _volume > 2 * float(front_volume):
            condition += 1
        if condition == 2:
            # 满足条件
            self.record_price(df_3mins)
            return {"side": "buy", "posSide": "long"}
        return False

    def get_short_signal_3min_confirm(self):
        """
        开空条件：
            1 上引线 大于实体
            2 vol是前K线的2倍
        """
        df_3mins = self._get_market_data(self.instId, self.bar1, limit='2')
        front_volume = df_3mins.iloc[0, :]['volume']
        row2 = df_3mins.iloc[-1, :]
        condition = 0
        _volume = float(row2['volume'])
        _close = float(row2['close'])
        _open = float(row2['open'])
        _high = float(row2['high'])
        entity = abs(_close - _open)
        down_wick = _high - max(_close, _open)
        # 引线大于实体，
        if down_wick > entity:
            condition += 1
        if _volume > 2 * float(front_volume):
            condition += 1
        if condition == 2:
            # 满足条件
            self.record_price(df_3mins)
            return {"side": "sell", "posSide": "short"}
        return False

    def record_price(self, df):
        pd.set_option("display.max_columns", None)
        pd.set_option('display.width', 100)
        self.log.info(df.tail(2))
        print(df.tail(2))

    def stop_order(self):
        """
        实时价格突破60MA. 且超过1个ATR值，平仓止盈
         """
        ma = int(re.findall(r"\d+", self.ma)[0])
        while True:
            time.sleep(1)
            self.log.info('等待止盈信号')
            print('等待止盈信号')
            self.df = self._get_candle_data(self.instId, self.bar2)
            self.df[self.ma] = self.df['close'].rolling(ma).mean()

            check_flag = self.check_price_to_ma(self.df)
            if check_flag:
                self.close_positions_all()
                self.has_order = False
                return self.has_order
            self.has_order = self.get_positions()
            if not self.has_order:
                # 已经触发了止损
                self.log.info('止损.......')
                print('止损.......')
                self.has_order = False
                return self.has_order


    def check_price_to_ma(self, df):
        # 实时价格突破60MA
        row = df.iloc[-1, :]
        ma = float(row[self.ma])
        high = float(row['high'])
        low = float(row['low'])
        # last = row['close']
        ma = 1425
        if high >= ma and low <= ma:
            atr = self.get_atr_data()
            if self.side == 'buy':
                if ma - low >= atr:
                    return True
            else:
                if high - ma >= atr:
                    return True
        return False


    def get_history_1h(self):
        self.df = self._get_market_data(self.instId, self.bar2)
        ma = int(re.findall(r"\d+", self.ma)[0])
        self.df[self.ma] = self.df['close'].rolling(ma).mean()


    def ready_order(self, posSide, side, sz):
        # isolated cross保证金模式.全仓, market：市价单  limit：限价单 post_only：只做maker单
        # sz 委托数量
        para = {
            "instId": self.instId,
            "tdMode": self.tdMode,
            "ccy": 'USDT',
            'side': side,
            'ordType': 'market',
            'sz': sz,
            'px': '',
            'posSide': posSide
        }

        result = self.tradeAPI.place_order(**para)
        ordId, sCode, sMsg= self.check_order_result_data(result, 'ordId')
        if sCode == "0":
            # 获取持仓信息
            # self.get_order_details(self.instId, ordId)
            self.has_order = self.get_positions()
            self.order_times += 1
            self.log.info('开仓成功！！！！！！')
        else:
            self.log.error('place_order error!!!!')
            self.has_order = False
        if self.has_order:
            # 设置止损止盈
            self.set_place_algo_order_oco()
            self.has_order = True

    def get_atr_data(self):
        try:
            self.mybalance = self.get_my_balance()
            # 或者atr值， 前20天波动值
            new_df = self.df.tail(20).copy()
            tr_lst = []
            new_df['tr'] = pd.to_numeric(new_df['high']) - pd.to_numeric(new_df['low'])
            atr = new_df['tr'].mean()
            return atr
        except:
            self.log.error('get ATR  error!!!!!!!!!!!!!!!!!!!!')


    def get_3_min_data(self):
        result = self.marketAPI.get_history_candlesticks(self.instId, limit="2")
        data_lst = result.get("data")
        columns_lst = ['time', 'open', 'high', 'low', 'close', 'volume', 'volCcy']
        self.df_3mins = pd.DataFrame(data_lst, columns=columns_lst)
        return self.df_3mins

    def get_3min_data_history(self):
        file_path = '../history_data/history_3m.csv'
        df = pd.read_csv(file_path, sep=',', parse_dates=['time'])
        df.set_index(['time'], inplace=True)

    def price_to_ma(self, p, ma, pre_norm=0.01):
        # 2 判断价格接近均线 %1 附近，
        pre = abs(float(p) - float(ma)) / float(ma)
        if pre <= pre_norm:
            return True
        return False

    def get_order_details(self, instId, ordId):
        result = self.tradeAPI.get_orders(instId, ordId)
        self.order_details = result.get('data')[0]
        avgPx = self.order_details.get('avgPx')
        state = self.order_details.get('state')
        side = self.order_details.get('side')
        # state = self.order_details.get('state')
        msg = '%s 开仓成功，均价：%s, 状态：%s, 方向：%s' % (instId, avgPx, state, side)
        self.log.info(msg)

    def set_place_algo_order_price(self):
        """ 设置止损止盈价格
            -1是市价止盈止损

            止损（ %5 * 账户资金 ） 除以 （ 3 * 建仓单位）
        """
        p = (0.05 * self.mybalance) / (3 * self.sz / 100)
        if self.order_lst:
            for data in self.order_lst:
                avgPx = data.get('avgPx')
                posSide = data.get('posSide')
                if posSide == 'long':
                    # tp = str(float(avgPx) + p)
                    tp = str(float(avgPx) * 10)
                    sl = str(float(avgPx) - p)
                else:
                    # tp = str(float(avgPx) - p)
                    tp = str(float(avgPx) / 10)
                    sl = str(float(avgPx) + p)
                # -1 为市价平仓
                p2 = "-1"
                price_para = {
                    "tpTriggerPx": tp,
                    "tpOrdPx": p2,
                    "slTriggerPx": sl,
                    "slOrdPx": p2
                }
                # msg = "止损止盈设置成功， 止盈触发价：%s, 止损触发价： %s， 市价平仓" % (tp, sl)
                # self.log.info(msg)
                return price_para
        else:
            self.log.error("no order details!!!*******************************")
            return

    def set_place_algo_order_oco(self, tpTriggerPx='', tpOrdPx='', slTriggerPx='', slOrdPx=''):
        """策略委托下单
        ordType:
            conditional：单向止盈止损
            oco：双向止盈止损
            trigger：计划委托
            move_order_stop：移动止盈止损
            iceberg：冰山委托
            twap：时间加权委托

        tpTriggerPx 止盈触发价，如果填写此参数，必须填写 止盈委托价
        tpOrdPx 止盈委托价，如果填写此参数，必须填写 止盈触发价, 委托价格为-1时，执行市价止盈
        slTriggerPx 止损触发价
        slOrdPx 止损委托价
        tpTriggerPxType = 'last' 最新价格
        """
        side = {"long": "sell", "short": "buy"}.get(self.posSide)
        price_para = self.set_place_algo_order_price()

        try:
            # result = self.tradeAPI.place_algo_order(self.instId, self.tdMode, self.side, ordType=self.ordType,
            #                                         sz=self.sz, posSide=self.posSide, tpTriggerPx=tpTriggerPx, tpOrdPx=tpOrdPx,
            #                                         slTriggerPx=slTriggerPx, slOrdPx=slOrdPx,
            #                                         tpTriggerPxType='last', slTriggerPxType='last')

            result = self.tradeAPI.place_algo_order(self.instId, self.tdMode, side, ordType=self.ordType,
                                                    sz=self.sz, posSide=self.posSide, **price_para,
                                                    tpTriggerPxType='last', slTriggerPxType='last')
        except Exception as e:
            self.log.error("委托单错误")
            self.log.error(e)
            return
        algoId, sCode, msg = self.check_order_result_data(result, "algoId")
        if sCode == "0":
            # 事件执行结果的code，0代表成功
            self.algoID = algoId
        else:
            # 事件执行失败时的msg
            self.log.error("止损止盈设置错误，，，%s" % msg)
        # 撤销策略委托订单
        # result = tradeAPI.cancel_algo_order([{'algoId': '297394002194735104', 'instId': 'BTC-USDT-210409'}])

    def check_signal1(self):
        print('等待%s信号....................' % self.bar2)

        # 1 首先判断是否处于趋势之中
        self.trend_analyze()
        signal_trend = self.set_signal_1h()
        # signal_trend = 'short'
        return signal_trend


    def check_signal2(self):
        while True:
            time.sleep(1)
            print('判断价格是否接近均线 %1 附近....................')
            # self.log.info('判断价格接近均线 %1 附近')
            # 2 判断价格接近均线 %1 附近，
            ma = self.df.iloc[-1, :][self.ma]
            # 获取现在的价格
            self.instId_detail = self._get_ticker(self.instId)
            last_p = self.instId_detail.get('last')
            # 2 判断价格接近均线 %1 附近，
            signal2 = self.price_to_ma(last_p, ma)
            # signal2 = True
            if signal2:
                return True

    """
    def check_signal2(self):
        print('判断价格接近均线 %1 附近....................')
        # self.log.info('判断价格接近均线 %1 附近')
        # 2 判断价格接近均线 %1 附近，
        ma = self.df.iloc[-1, :][self.ma]
        # 获取现在的价格
        self.instId_detail = self._get_ticker(self.instId)
        last_p = self.instId_detail.get('last')
        # 2 判断价格接近均线 %1 附近，
        signal2 = self.price_to_ma(last_p, ma)
        signal2 = True
        if signal2:
            Timer(1, self.check_signal2).cancel()
            return True
        # tian看
        Timer(1, self.check_signal2).start()
    """

    def check_signal3(self, signal1):
        """
            检测3分钟信号
            如果3个大周期还未出现信号，则不再判断 退出程序
        """
        t_num = self.get_time_inv(self.bar2)
        for t in range(t_num):
            self.log.info("循环检测%s信号, 第%s次" % (self.bar1, t))
            print("循环检测%s信号, 第%s次" % (self.bar1, t))
            if signal1 == 'long':
                # 开多信号
                signal_order_para = self.get_long_signal_3min_confirm()
            elif signal1 == 'short':
                # 开空信号
                signal_order_para = self.get_short_signal_3min_confirm()
            else:
                signal_order_para = False
            if signal_order_para:
                self.log.info('满足3分钟信号')
                return signal_order_para

            time.sleep(1)

        # 没出现信号
        self.log.info('3个大周期仍然没有出现没有3分钟信号 ，结束程序')
        print('3个大周期仍然没有出现没有3分钟信号 ，结束程序')
        raise

    def get_time_inv(self, t):
        t_num = int(re.findall(r"\d+", t)[0])
        if 'H' in t:
            t_num = t_num * 60 * 60
        elif 'm' in t:
            t_num = t_num * 60
        else:
            pass
        return t_num


if __name__ == '__main__':
    ma = "MA10"
    my_ma_trade = MaTrade(ma)
    my_ma_trade.start_my_trade()


