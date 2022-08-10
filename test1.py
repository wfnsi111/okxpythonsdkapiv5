# -*- coding: utf-8 -*-

from basetrade.basetrade import BaseTrade
from importlib import import_module


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
        self.has_order = False  # 设置一个参数，只持仓1笔交易， 有持仓的适合 就不在开仓
        self.set_initialization_account()

    def set_initialization_account(self):
        """ 初始化账户 """
        result = self.accountAPI.get_position_mode('long_short_mode')
        result = self.accountAPI.set_leverage(instId='ETH-USDT-SWAP', lever='10', mgnMode='cross')

    def start_tarde(self, strategy, **kwargs):
        instId = 'ETH-USDT-SWAP'
        para = {
            "instId": instId,
            "tdMode": self.tdMode,
            "ccy": 'USDT',
            'side': 'buy',
            'ordType': 'market',
            'sz': 2000,
            'px': '',
            'posSide': 'long'
        }
        result = self.tradeAPI.place_order(**para)
        ordId, sCode, sMsg = self.check_order_result_data(result, 'ordId')
        result = self.get_my_balance()
        self.log.info("start trading...............................")
        result = self.tradeAPI.get_orders_history('SWAP', limit='1')
        result = self.tradeAPI.get_orders_history('SWAP', limit='1')
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
    kw = {
        'instId': 'ETH-USDT-SWAP',
        "ma": "MA60",
        "bar1": '3m',
        "bar2": '12H',
        "ma_percent": 0.005
    }
    my_trade = MyTrade(api_key, secret_key, passphrase, use_server_time, flag)
    my_trade.start_tarde(strategy, **kw)
