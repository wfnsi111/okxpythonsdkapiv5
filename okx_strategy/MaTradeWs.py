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
import asyncio
import json
import websockets

api_key = "47473a01-7149-4deb-ac31-ee54a3afc124"
secret_key = "79AADC7A194FD4548AFEB12AC9F78D13"
passphrase = "Lch798503@"
# flag是实盘与模拟盘的切换参数
# flag = '1'  # 模拟盘 demo trading
flag = '0'  # 实盘 real trading


# df['gtime']=pd.to_datetime(df['gtime'],unit='s'))


class MaTradeWs(BaseTrade):
    def __init__(self, api_key=None, secret_key=None, passphrase=None, use_server_time=False, flag='1', **kwargs):
        super().__init__(api_key, secret_key, passphrase, use_server_time, flag)
        self.df = None
        self.df_3mins = None
        self.stop_loss = 0
        self.flag = flag
        self.ma = kwargs.get('ma')
        self.instId = kwargs.get('instId')
        self.bar1 = kwargs.get('bar1')
        self.bar2 = kwargs.get('bar2')
        self.ma_percent = kwargs.get('ma_percent', 0.01)  # 价格接近均线的百分比
        self.big_bar_time = kwargs.get('big_bar_time', 3)  # 大周期循环次数
        self.last_price_data = []
        self.signal_order_para = None
        self.signal1 = False
        self.signal2 = False
        self.signal3 = False

    async def subscribe_without_login(self, url, channels):
        l = []
        while True:
            try:
                async with websockets.connect(url) as ws:
                    sub_param = {"op": "subscribe", "args": channels}
                    sub_str = json.dumps(sub_param)
                    await ws.send(sub_str)
                    print(f"send: {sub_str}")
                    while True:
                        try:
                            res = await asyncio.wait_for(ws.recv(), timeout=25)
                        # except (asyncio.TimeoutError, websockets.exceptions.ConnectionClosed) as e:
                        except Exception as e:
                            try:
                                await ws.send('ping')
                                res = await ws.recv()
                                print(res)
                                continue
                            except Exception as e:
                                print("连接关闭，正在重连……")
                                break

                        # print(self.get_timestamp() + res)
                        res = eval(res)
                        # self.last_price_data = eval(res)
                        if 'event' in res:
                            continue

                        if 'msg' in res:
                            self.log.error(res .get('msg'))
                            break

                        self.start_analyze(res, signal=1)

            except Exception as e:
                print(e)
                print("连接断开，正在重连……")
                continue

    def start_analyze(self, price_data, signal):
        self.has_order = self.get_positions()
        if self.has_order:
            self.has_order = self.stop_order()

        if self.stop_loss == 2:
            # 止损了2次， 退出程序
            self.log.info('止损2次，退出程序')
            print('止损2次，退出程序')
            raise

        if self.stop_loss == 1:
            # 止损了1次， 直接检测信号3
            if self.signal_order_para:
                self.log.info('3分钟满足开仓条件，准备开仓')
                # 设置头寸
                atr = self.get_atr_data()
                self.sz = int(0.05 * self.mybalance / atr * 100)
                self.posSide = self.signal_order_para.get('posSide')
                self.side = self.signal_order_para.get('side')
                # 开仓
                self.ready_order(self.posSide, self.side, self.sz)

        # 判断信号1
        if not self.signal1:
            # 判断前面的K线是否满足条件
            self.signal1 = self.check_signal1()
            if not self.signal1:
                # 收线之后再次判断
                self.log.info('%s震荡中....................' % self.bar2)
                self.wait_big_next_bar(price_data)
                return 1

        self.signal2 = self.check_signal2(price_data)

        if not self.signal2:
            # 如果没有信号2 ，
            return 2

        if self.signal2:
            self.log.info('价格接近均线 %1 附近')
            self.signal_order_para = self.check_signal3(self.signal1)
            # signal_order_para = {"side": "buy", "posSide": "long"}
            # signal_order_para = {"side": "sell", "posSide": "short"}
            if self.signal_order_para:
                self.log.info('3分钟满足开仓条件，准备开仓')
                # 设置头寸
                atr = self.get_atr_data()
                self.sz = int(0.05 * self.mybalance / atr * 100)
                self.posSide = self.signal_order_para.get('posSide')
                self.side = self.signal_order_para.get('side')
                # 开仓
                self.ready_order(self.posSide, self.side, self.sz)

    def start_my_trade(self):
        print('MaTrade 初始化中........')
        self.has_order = self.get_positions()
        url = "wss://ws.okx.com:8443/ws/v5/public"
        channels = [{"channel": 'candle' + self.bar2, "instId": self.instId}]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.subscribe_without_login(url, channels))

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
        ordId, sCode, sMsg = self.check_order_result_data(result, 'ordId')
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
        print('等待信号1....................')

        # 1 首先判断是否处于趋势之中
        self.trend_analyze()
        signal_trend = self.set_signal_1h()
        # signal_trend = 'short'
        return signal_trend

    def check_signal2(self, price_data):
        print('正在判断信号2....................')
        # self.log.info('判断价格接近均线 %1 附近')
        # 2 判断价格接近均线 %1 附近，
        ma = self.df.iloc[-1, :][self.ma]
        # 2 判断价格接近均线 %1 附近，
        last = price_data.get('data')[0][4]
        signal2 = self.price_to_ma(last, ma, self.ma_percent)
        # signal2 = True
        if signal2:
            return True
        return False

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
        print("信号2已确认！")
        for t in range(t_num):
            self.log.info("循环检测信号3, 持续时间%s秒" % t)
            # print("\r"+"检测信号3, 持续时间%s秒" % t, flush=True)
            print("检测信号3, 持续时间%s秒" % t)
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

    def wait_big_next_bar(self, price_data):
        pass

