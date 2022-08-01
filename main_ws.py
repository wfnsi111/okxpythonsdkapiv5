# -*- coding: utf-8 -*-

dic1 = {"buy": "long", "sell": "short"}
api_key = "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2"
secret_key = "A23C7CEB8046F39369CF73BDEBE985F5"
passphrase = "Kangkang1_"
# flag是实盘与模拟盘的切换参数
flag = '1'  # 模拟盘 demo trading
# flag = '0'  # 实盘 real trading


class MyTrade():
    def __init__(self, instId, ma):
        self.instId = instId
        self.flag = flag
        self.signal = 'buy'
        self.trade_ok = False
        self.posSide = ''
        self.sz = "2"
        self.ma = ma
        self.order_details = None
        self.tdMode = 'cross'
        self.ordType = 'oco'
        self.has_order = False  # 设置一个参数，只持仓1笔交易， 有持仓的适合 就不在开仓


    def start_tarde(self):
        self.has_order = self.get_positions()
        strategy_obj = self.choose_strategy()
        # 如果有仓位 寻找平仓点位
        if self.has_order:
            self.trade_close_positions()
            # pass
        if not self.has_order:
            signal_0 = strategy_obj.start_my_trade()
            signal_0 = {"side": "buy",
                    "posSide": "long"
                    }
            # 是否满足策略的信号， 如果满足信号， 开仓
            if signal_0:
                self.ready_order(signal_0)
            else:
                pass

        # my_balance = self.get_balance()
        # my_posotions = self.get_positions()
        # if not my_posotions:
        #     self.ready_order()
            # self.trade_close_positions()

    def get_balance(self):
        """获取账户余额  availEq """
        result = self.accountAPI.get_account('USDT')
        data = result.get('data', [])[0].get('details')[0]
        my_balance = data.get('availEq', '')
        return my_balance

    def get_positions(self):
        result = self.accountAPI.get_positions('SWAP')
        data_list = result.get('data', [])
        for item in data_list:
            if not item:
                return False
            else:
                return True

    def ready_order(self, signal_0):
        # isolated cross保证金模式.全仓, market：市价单  limit：限价单 post_only：只做maker单
        # sz 委托数量
        para = {
            "instId": self.instId,
            "tdMode": self.tdMode,
            "ccy": 'USDT',
            'side': signal_0.get('side'),
            'ordType': 'market',
            'sz': self.sz,
            'px': '',
            'posSide': signal_0.get('posSide')

        }
        result = self.tradeAPI.place_order(**para)
        data = result.get('data')[0]
        clOrdId = data.get("clOrdId")
        sCode = data.get("sCode")     # sCode	String	事件执行结果的code，0代表成功
        if sCode == "0":
            ordId = data.get("ordId")
            self.trade_ok = True
            # 获取订单信息
            self.get_order_details(self.instId, ordId)
        else:
            sMsg = data.get("sMsg")
            self.trade_ok = False
        if self.trade_ok:
            # 设置止损止盈
            self.set_place_algo_order_oco()



    def trade_close_positions(self):
        """ 市价平仓 """
        self.posSide = {"buy": "long", "sell": "short"}.get(self.signal, '')
        para = {
            "instId": self.instId,
            "mgnMode": self.tdMode,
            "ccy": "USDT",
            "posSide": self.posSide
        }
        result = self.tradeAPI.close_positions(**para)
        data = result.get("data")[0]
        self.has_order = False

    def choose_strategy(self, strategy=''):
        from okx_strategy.MaTrade import ma_trade
        ma = "MA10"
        my_ma_trade = ma_trade(ma)
        return my_ma_trade

    def get_order_details(self, instId, ordId):
        result = self.tradeAPI.get_orders(instId, ordId)
        self.order_details = result.get('data')[0]

    def set_place_algo_order_price(self, p=50.0):
        """ 设置止损止盈价格
            -1是市价止盈止损
        """
        # 测试 BTC成交均价上下 50个点止损止盈
        if self.order_details:
            avgPx = self.order_details.get('avgPx')
            p = float(p)
            tp = str(float(avgPx) + p)
            sl = str(float(avgPx) - p)
            price_para = {
                "tpTriggerPx": tp,
                "tpOrdPx": "-1",
                "slTriggerPx": sl,
                "slOrdPx": "-1"
            }
            return price_para
        else:
            pass
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
        # result = self.tradeAPI.place_algo_order(self.instId, self.tdMode, self.signal, ordType=self.ordType,
        #                                         sz=self.sz, posSide=self.posSide, tpTriggerPx=tpTriggerPx, tpOrdPx=tpOrdPx,
        #                                         slTriggerPx=slTriggerPx, slOrdPx=slOrdPx,
        #                                         tpTriggerPxType='last', slTriggerPxType='last')
        result = self.tradeAPI.place_algo_order(self.instId, self.tdMode, side, ordType=self.ordType,
                                                sz=self.sz, posSide=self.posSide, **price_para,
                                                tpTriggerPxType='last', slTriggerPxType='last')

        data_lst = result.get('data')
        for data in data_lst:
            # algoI	策略委托单ID
            algoId = data.get("algoId")
            sCode = data.get("sCode")
            if sCode == "0":
                # 事件执行结果的code，0代表成功
                print("止损止盈设置成功")
            else:
                # 事件执行失败时的msg
                sMsg = data.get("sMsg")
        # 撤销策略委托订单
        # result = tradeAPI.cancel_algo_order([{'algoId': '297394002194735104', 'instId': 'BTC-USDT-210409'}])

    def set_place_algo_order_oco_trigger(self):
        """计划委托"""
        pass

    def _cancel_algo_order(self):
        """撤销策略委托订单"""
        pass

    def check_order_res_data(self, data):
        pass


if __name__ == '__main__':
    strategy = 'MA'
    instId = 'BTC-USDT-SWAP'
    ma = "MA10"
    my_trade = MyTrade(instId, ma)
    my_trade.start_tarde()
