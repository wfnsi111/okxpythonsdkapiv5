import time

import okx.Account_api as Account
import okx.Trade_api as Trade
# from websocket_example import subscribe_without_login
# import asyncio
# import websockets
from basetrade.basetrade import BaseTrade
from importlib import import_module

dic1 = {"buy": "long", "sell": "short"}


class MyTrade(BaseTrade):
    def __init__(self, instId, api_key, secret_key, passphrase, use_server_time=False, flag="1"):
        super().__init__(api_key, secret_key, passphrase)

        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.instId = instId
        self.flag = flag
        self.side = 'buy'
        self.trade_ok = False
        self.posSide = ''
        self.sz = "2"
        self.order_details = None
        self.tdMode = 'cross'
        self.ordType = 'oco'
        self.has_order = False  # 设置一个参数，只持仓1笔交易， 有持仓的适合 就不在开仓
        self.algoID = ''

    def start_tarde(self, strategy, ma=None, bar=None):
        self.log.info("start trading...............................")
        strategy_obj = self.choose_strategy(strategy, ma=ma, bar=bar)
        try:
            strategy_obj.start_my_trade()
        except Exception as e:
            self.log.error(e)

    def choose_strategy(self, strategy='', ma=None, bar=None):
        module = import_module('okx_strategy.%s' % strategy)
        cls = getattr(module, strategy)
        obj = cls(instId, ma, bar, self.api_key, self.secret_key, self.passphrase)
        return obj


    def set_place_algo_order_oco_trigger(self):
        """计划委托"""
        pass

    def _cancel_algo_order(self):
        """撤销策略委托订单"""
        pass


    # def get_last_traded_price(self):
    #     ws_url = "wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"
    #     channels = [{"channel": "tickers", "instId": self.instId}]
    #
    #     loop = asyncio.get_event_loop()
    #     loop.run_until_complete(subscribe_without_login(ws_url, channels))
    #     # loop.close()


if __name__ == '__main__':
    api_key = "f76a1e05-cc56-43fd-aa6a-88aa3e51b6a2"
    secret_key = "A23C7CEB8046F39369CF73BDEBE985F5"
    passphrase = "Kangkang1_"
    # flag是实盘与模拟盘的切换参数
    flag = '1'  # 模拟盘 demo trading
    # flag = '0'  # 实盘 real trading
    use_server_time = False
    strategy = 'MaTrade'
    instId = 'ETH-USDT-SWAP'
    ma = "MA60"
    bar1 = '3m'
    bar2 = '15m'
    my_trade = MyTrade(instId, api_key, secret_key, passphrase, use_server_time, flag)
    my_trade.start_tarde(strategy, ma, [bar1, bar2])
