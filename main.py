# -*- coding: utf-8 -*-

from basetrade.basetrade import BaseTrade
from importlib import import_module
import re


class MyTrade(BaseTrade):
    def __init__(self, api_key, secret_key, passphrase, use_server_time=False, flag="1"):
        super().__init__(api_key, secret_key, passphrase, use_server_time, flag)
        self.passphrase = passphrase
        self.api_key = api_key
        self.secret_key = secret_key
        self.use_server_time = use_server_time
        self.flag = flag
        self.side = 'buy'
        self.trade_ok = False
        self.posSide = ''
        self.sz = "2"
        self.order_details = None
        self.tdMode = 'cross'
        self.ordType = 'oco'
        self.has_order = False  # 设置一个参数，只持仓1笔交易， 有持仓的时候 就不在开仓

    def start_tarde(self, strategy, **kwargs):
        self.log.info("start trading...............................")
        print('CyTrade 初始化中........')
        strategy_obj = self.choose_strategy(strategy, **kwargs)
        try:
            strategy_obj.start_my_trade()
        except Exception as e:
            self.log.error(e)

    def choose_strategy(self, strategy='', **kwargs):
        module = import_module('okx_strategy.%s' % strategy)
        cls = getattr(module, strategy)
        obj = cls(self.api_key, self.secret_key, self.passphrase, self.use_server_time, self.flag, **kwargs)
        return obj

    def set_place_algo_order_oco_trigger(self):
        """计划委托"""
        pass

    def _cancel_algo_order(self):
        """撤销策略委托订单"""
        pass


def get_aip_key_():
    from conf.api_key_conf import get_aip_key
    my_aip_key = get_aip_key()
    api_key = my_aip_key.get('api_key')
    secret_key = my_aip_key.get('secret_key')
    passphrase = my_aip_key.get('passphrase')
    flag = my_aip_key.get('flag')
    return api_key, secret_key, passphrase, flag


if __name__ == '__main__':
    api_key, secret_key, passphrase, flag = get_aip_key_()
    use_server_time = False
    strategy = 'MaTrade'

    bar2 = '1H'

    kw = {
        'instId': 'ETH-USDT-SWAP',
        "ma": "MA60",
        "bar2": bar2,
        "big_bar_time": 3,
    }

    my_trade = MyTrade(api_key, secret_key, passphrase, use_server_time, flag)
    my_trade.start_tarde(strategy, **kw)
