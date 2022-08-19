# -*- coding: utf-8 -*-

"""

信号1 趋势中
信号2 大周期接近均线
信号3 小周期引线和成交量达到要求

"""

import pandas as pd
import mplfinance as mpf
import time
from basetrade.basetrade import BaseTrade
import re
from conf.ma_trade_args import args_dict


class MaTrade(BaseTrade):
    def __init__(self, api_key=None, secret_key=None, passphrase=None, use_server_time=False, flag='1', **kwargs):
        super().__init__(api_key, secret_key, passphrase, use_server_time, flag)
        self.df = None
        self.df_3mins = None
        self.stop_loss = 0
        self.flag = flag
        self.ma = kwargs.get('ma')
        self.instId = kwargs.get('instId')
        self.bar2 = kwargs.get('bar2')
        self.big_bar_time = kwargs.get('big_bar_time', 3)
        self.signal_order_para = None
        self.signal1 = False
        self.signal2 = False
        self.signal3 = False
        self.ma_percent, self.bar1, self.max_stop_loss, self.set_profit, self.risk_control = self.set_args(self.bar2)

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
        time.sleep(2)
        i = 1
        self.has_order = self.get_positions()
        while True:
            time.sleep(1)
            # time.sleep(60)
            # 检测持仓
            # self.has_order = self.get_positions()
            if self.has_order:
                self.has_order = self.stop_order(profit=self.set_profit)
                # if self.has_order:
                #     continue

            if self.stop_loss == self.max_stop_loss:
                # 止损了2次， 退出程序
                self.log.info('止损%s次，退出程序' % self.max_stop_loss)
                print('止损%s次，退出程序' % self.max_stop_loss)
                break

            if self.stop_loss < self.max_stop_loss and self.stop_loss > 0:
                # 止损了1次， 直接检测信号3
                self.signal_order_para = self.check_signal3(self.signal1)
                if self.signal_order_para:
                    print()
                    print('已检测到信号3.。。。')
                    # 开仓
                    self.ready_order()
                    continue

            # 判断信号1
            print("\r" + "等待%s信号" % self.bar2 + '.' * i + ' ' * (7 - i), flush=True, end='')
            i += 1
            if i == 7:
                i = 1
            self.signal1 = self.check_signal1()
            if not self.signal1:
                # print('等待信号1....................')
                continue

            print()
            print('信号1已确认!')
            print('周期行情处于趋势之中')
            self.log.info('信号1已确认!')

            # 判断信号2
            self.signal2 = self.check_signal2()
            if self.signal2:
                self.signal_order_para = self.check_signal3(self.signal1)
                # signal_order_para = {"side": "buy", "posSide": "long"}
                # signal_order_para = {"side": "sell", "posSide": "short"}
                if self.signal_order_para:
                    # 开仓
                    print('已检测到信号3.。。。')
                    self.ready_order()

    def set_my_position(self):
        # 设置头寸
        atr = self.get_atr_data(self.df, 20)
        self.mybalance = self.get_my_balance()
        currency = self.risk_control * self.mybalance / atr
        sz = self.currency_to_sz(self.instId, currency)
        if sz < 1:
            print('仓位太小， 无法开仓 ---> *** %s张 ***' % sz)
            self.log.error('仓位太小， 无法开仓')
            raise
        return int(sz)

    def trend_analyze(self, c_length=10):
        '''
        第一步： 判断趋势
            10根K线连续处于均线以下
        '''
        self.df = self._get_market_data(self.instId, self.bar2, [self.ma])
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
        df_3mins = self._get_market_data(self.instId, self.bar1, vol_ma=20, limit='100')
        front_volume = df_3mins.iloc[-2, :]['volume']
        row2 = df_3mins.iloc[-1, :]
        bar1_close = float(row2['close'])
        _volume = float(row2['volume'])
        _open = float(row2['open'])
        _low = float(row2['low'])
        entity = abs(bar1_close - _open)
        down_wick = min(bar1_close, _open) - _low
        vol_ma = float(row2['vol_ma'])
        # 引线, 成交量，价格
        if down_wick > entity:
            if _volume > 2 * float(front_volume):
                if _volume >= 2 * vol_ma:
                    code = self.check_price_to_ma_pec(bar1_close)
                    if code:
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
        df_3mins = self._get_market_data(self.instId, self.bar1, vol_ma=20, limit='100')
        front_volume = df_3mins.iloc[-2, :]['volume']
        row2 = df_3mins.iloc[-1, :]
        bar1_close = float(row2['close'])
        _volume = float(row2['volume'])
        self.bar1_close = bar1_close
        _open = float(row2['open'])
        _high = float(row2['high'])
        entity = abs(bar1_close - _open)
        down_wick = _high - max(bar1_close, _open)
        vol_ma = float(row2['vol_ma'])
        # 引线, 成交量，价格
        if down_wick >= entity:
            if _volume >= 2 * float(front_volume):
                if _volume >= 2 * vol_ma:
                    code = self.check_price_to_ma_pec(bar1_close)
                    if code:
                        # 满足条件
                        self.record_price(df_3mins)
                        return {"side": "sell", "posSide": "short"}
        return False

    def record_price(self, df):
        pd.set_option("display.max_columns", None)
        pd.set_option('display.width', 100)
        self.log.info('信号出现， 准备开仓')
        self.log.info(df.tail(2))
        print('信号出现， 准备开仓')
        print(df.tail(2))

    '''
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
                self.stop_loss = 0
                return self.has_order
            self.has_order = self.get_positions()
            if not self.has_order:
                # 已经触发了止损
                self.log.info('止损.......')
                print('止损.......')
                self.has_order = False
                self.stop_loss += 1
                return self.has_order
    '''

    def stop_order(self, profit):
        self.log.info('等待止盈信号')
        i = 0
        if profit:
            while True:
                time.sleep(30)
                i += 1
                print("\r" + "等待止盈信号" + '.' * i + ' ' * (7 - i), flush=True, end='')
                if i == 6:
                    i = 0
                result = self.tradeAPI.get_orders_history('SWAP', limit='1')
                order_data = result.get('data')[0]
                para = {"long": "sell", "short": "buy"}
                if para.get(order_data.get('posSide')) == order_data.get('side'):
                    # 平仓单
                    self.has_order = self.get_positions()
                    if self.has_order:
                        self.log.error('止损止盈检查错误， 订单ID%s' % order_data.get('ordId'))
                    if float(order_data.get('pnl')) >= 0:
                        print('止盈')
                        self.log.info('止盈')
                        self.stop_loss = 0
                    else:
                        print('亏损')
                        self.log.info('亏损')
                        self.stop_loss += 1
                        if self.stop_loss < self.max_stop_loss:
                            bar1_num = int(re.findall(r"\d+", self.bar1)[0])
                            print('止损啦！本人需要冷静片刻。。。')
                            self.log.info('止损， 休息%s在继续运行' % self.bar1)
                            time.sleep(bar1_num*60)
                    return self.has_order

        else:
            ma = int(re.findall(r"\d+", self.ma)[0])
            # 实时价格突破60MA. 且超过1个ATR值，平仓止盈
            while True:
                time.sleep(1)
                # self.log.info('等待止盈信号')
                print('等待止盈信号')
                self.df = self._get_candle_data(self.instId, self.bar2)
                self.df[self.ma] = self.df['close'].rolling(ma).mean()
                check_flag = self.check_price_to_ma(self.df)
                if check_flag:
                    self.close_positions_all()
                    self.has_order = False
                    self.stop_loss = 0
                    return self.has_order

                self.has_order = self.get_positions()
                if not self.has_order:
                    # 已经触发了止损
                    self.log.info('止损.......')
                    print('止损.......')
                    self.has_order = False
                    self.stop_loss += 1
                    return self.has_order

    def check_price_to_ma(self, df):
        # 实时价格突破60MA
        row = df.iloc[-1, :]
        ma = float(row[self.ma])
        high = float(row['high'])
        low = float(row['low'])
        # last = row['close']
        if high >= ma and low <= ma:
            atr = self.get_atr_data(df, 20)
            if self.side == 'buy':
                if ma - low >= atr:
                    return True
            else:
                if high - ma >= atr:
                    return True
        return False

    def check_price_to_ma_pec(self, bar1_close):
        # 实时价格是否接近均线百分比附近
        df = self._get_candle_data(self.instId, self.bar2, [self.ma])
        row = df.iloc[-1, :]
        ma = float(row[self.ma])
        # high = float(row['high'])
        # low = float(row['low'])
        last_p = float(row['close'])
        code = self.price_to_ma(bar1_close, ma, self.ma_percent)
        # if code:
        #     print('价格在均线附近，准备开仓')
        #     self.log.info('价格在均线附近，准备开仓')
        # else:
        #     print('价格远离均线，信号无效，重新检测中')
        #     self.log.info('价格远离均线，信号无效，重新检测中')
        return code

    def ready_order(self):
        # isolated cross保证金模式.全仓, market：市价单  limit：限价单 post_only：只做maker单
        # sz 委托数量
        self.set_initialization_account(self.instId, lever='50', mgnMode='cross')
        self.sz = self.set_my_position()
        self.posSide = self.signal_order_para.get('posSide')
        self.side = self.signal_order_para.get('side')
        para = {
            "instId": self.instId,
            "tdMode": self.tdMode,
            "ccy": 'USDT',
            'side': self.side,
            'ordType': 'market',
            'sz': self.sz,
            'px': '',
            'posSide': self.posSide
        }

        result = self.tradeAPI.place_order(**para)
        ordId, sCode, sMsg= self.check_order_result_data(result, 'ordId')
        if sCode == "0":
            # 获取持仓信息
            # self.get_order_details(self.instId, ordId)
            self.has_order = self.get_positions()
            self.order_times += 1
            print('开仓成功！！！！！！')
            self.log.info('开仓成功！！！！！！')
        else:
            self.log.error('place_order error!!!!')
            self.has_order = False
        if self.has_order:
            # 设置止损止盈
            self.set_place_algo_order_oco()
            self.has_order = True

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

    def price_to_ma(self, p, ma, ma_percent=0.01):
        # 2 判断价格接近均线 %1 附近，
        pre = abs(float(p) - float(ma)) / float(ma)
        if pre <= ma_percent:
            return True
        return False

    def set_place_algo_order_price(self):
        """ 设置止损止盈价格
            -1是市价止盈止损

            止损（ %5 * 账户资金 ） 除以 （ 3 * 建仓单位）
        """
        p = (0.05 * self.mybalance) / (3 * self.sz / 10)
        if self.order_lst:
            for data in self.order_lst:
                avgPx = data.get('avgPx')
                posSide = data.get('posSide')
                if self.set_profit:
                    if posSide == 'long':
                        tp = str(float(avgPx) + int(self.set_profit) * p)
                        sl = str(float(avgPx) - p)
                    else:
                        tp = str(float(avgPx) - int(self.set_profit) * p)
                        sl = str(float(avgPx) + p)
                else:
                    if posSide == 'long':
                        tp = str(float(avgPx) * 2)
                        sl = str(float(avgPx) - p)
                    else:
                        tp = str(float(avgPx) / 2)
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
        # 1 首先判断是否处于趋势之中
        self.trend_analyze()
        signal1 = self.set_signal_1h()
        # signal1 = 'short'
        return signal1

    def check_signal2(self):
        self.log.info('正在判断信号2....................')
        i = 0
        while True:
            i += 1
            print("\r" + "正在判断信号2" + '.' * i + ' ' * (7 - i), flush=True, end='')
            if i == 6:
                i = 0
            time.sleep(2)
            # 获取现在的价格
            self.df = self._get_candle_data(self.instId, self.bar2, [self.ma])
            # 2 判断价格接近均线 %1 附近，
            row = self.df.iloc[-1, :]
            ma = row[self.ma]
            last_p = row['close']
            # 2 判断价格接近均线 %1 附近，
            signal2 = self.price_to_ma(last_p, ma, self.ma_percent)
            # signal2 = True
            if signal2:
                print()
                print("信号2已确认！")
                self.log.info("信号2已确认！")
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
        t_num = self.get_time_inv(self.bar2, self.big_bar_time)
        self.log.info("开始循环检测信号3")
        i = 0
        for t in range(t_num):
            i += 1
            print("\r"+"检测信号3, 持续时间%s秒" % t + '.' * i + ' ' * (7 - i), flush=True, end='')
            if i == 6:
                i = 0
            # print("检测信号3, 持续时间%s秒" % t)
            if signal1 == 'long':
                # 开多信号
                signal_order_para = self.get_long_signal_3min_confirm()
            elif signal1 == 'short':
                # 开空信号
                signal_order_para = self.get_short_signal_3min_confirm()
            else:
                signal_order_para = False
            # signal_order_para = {"side": "buy", "posSide": "long"}
            if signal_order_para:
                self.log.info('满足3分钟信号')
                return signal_order_para

            time.sleep(1)

        # 没出现信号
        self.log.info('未出现开仓信号 ，重新开始新一轮检测')
        print('未出现开仓信号 ，重新开始新一轮检测')
        raise

    def get_time_inv(self, t, big_bar_time):
        t_num = int(re.findall(r"\d+", t)[0])
        if 'H' in t:
            t_num = t_num * 60 * 60
        elif 'm' in t:
            t_num = t_num * 60
        elif 'D' in t:
            t_num = t_num * 60 * 60 * 24
        else:
            pass
        return t_num * big_bar_time

    def set_args(self, bar):
        data_dict = args_dict.get(bar, None)
        if data_dict is None:
            self.log.error('大周期错误')
            raise
        ma_percent = data_dict.get('ma_percent')
        bar1 = data_dict.get('bar1')
        max_stop_loss = data_dict.get('stop_loss')
        set_profit = data_dict.get('set_profit')
        risk_control = data_dict.get('risk_control')
        return ma_percent, bar1, max_stop_loss, set_profit, risk_control


if __name__ == '__main__':
    ma = "MA10"
    my_ma_trade = MaTrade(ma)
    my_ma_trade.start_my_trade()


