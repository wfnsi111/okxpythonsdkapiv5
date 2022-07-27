# -*- coding: utf-8 -*-

from Mylog.mylog import LoggerHandler
import time
import okx.Account_api as Account
import okx.Funding_api as Funding
import okx.Market_api as Market
import okx.Public_api as Public
import okx.Trade_api as Trade
import okx.status_api as Status
import okx.subAccount_api as SubAccount
import okx.TradingData_api as TradingData
import okx.Broker_api as Broker
import okx.Convert_api as Convert
import okx.FDBroker_api as FDBroker
import okx.Rfq_api as Rfq
import okx.TradingBot_api as TradingBot
import pandas as pd


class BaseTrade(object):
    def __init__(self, api_key, secret_key, passphrase, use_server_time=False, flag='1'):
        self.marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, True)
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, use_server_time, flag)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, use_server_time, flag)
        self.log = LoggerHandler()
        self.db = None
        self.side = 'buy'
        self.trade_ok = False
        self.posSide = ''
        self.sz = "2"
        self.tdMode = 'cross'
        self.ordType = 'oco'
        self.order_lst = []
        self.mybalance = 0
        self.instId_detail = {}
        self.has_order = None
        self.order_times = 0

    def timestamp_to_date(self, t):
        # 13位时间戳转日期
        timestamp = float(t)/1000
        timearray = time.localtime(timestamp)
        date = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
        return date

    def get_positions(self):
        result = self.accountAPI.get_positions('SWAP')
        self.order_lst = result.get('data', [])
        for item in self.order_lst:
            if not item:
                return False
            else:
                return True

    def check_order_result_data(self, data, flag_id=None):
        sMsg = ''
        try:
            data_list = data["data"]
        except:
            return False, False, sMsg
        for data in data_list:
            sCode = data.get("sCode", '')
            flag_id = data.get(flag_id, '')
            if sCode == "0":
                # 执行成功
                pass
            else:
                sMsg = data.get("sMsg")
                self.log.error(sMsg)
                return False, False, sMsg
            return flag_id, sCode, sMsg

    def close_positions_all(self):
        """ 市价平仓 """
        if not self.order_lst:
            self.get_positions()

        for item in self.order_lst:
            para = {
                "instId": item.get("instId"),
                'mgnMode': item.get('mgnMode'),
                "ccy": item.get('ccy'),
                "posSide": item.get('posSide'),
                'autoCxl': True
            }
            # self.posSide = {"buy": "long", "sell": "short"}.get(self.side, '')
            # 检测是否有委托 ，如果有委托， 先撤销委托，在平仓
            # self.algo = self.cancel_algo_order_(algoid)
            try:
                result = self.tradeAPI.close_positions(**para)
            except:
                self.log.error("平仓错误")
        self.has_order = False
        self.order_lst.clear()

    def _get_market_data(self, instId, bar, limit='100'):
        """ 获取历史K线数据 """
        result = self.marketAPI.get_history_candlesticks(instId, bar=bar, limit=limit)
        data_lst = result.get("data")
        new_data_lst = []
        columns_lst = ['date', 'open', 'high', 'low', 'close', 'volume', 'volCcy']
        # 按时间从小到大排序
        l = int(limit)
        for i in range(l, 0, -1):
            data_ = data_lst[i - 1]
            data_[0] = self.timestamp_to_date(data_[0])
            new_data_lst.append(data_)

        df_market_data = pd.DataFrame(new_data_lst, columns=columns_lst)
        df_market_data['date'] = pd.to_datetime(df_market_data['date'])
        df_market_data.set_index(['date'], inplace=True)
        return df_market_data

    def _get_candle_data(self, instId, bar, limit='100'):
        """ 获取K线数据 """
        result = self.marketAPI.get_candlesticks(instId, bar=bar, limit=limit)
        data_lst = result.get("data")
        new_data_lst = []
        columns_lst = ['date', 'open', 'high', 'low', 'close', 'volume', 'volCcy']
        # 按时间从小到大排序
        l = int(limit)
        for i in range(l, 0, -1):
            data_ = data_lst[i - 1]
            data_[0] = self.timestamp_to_date(data_[0])
            new_data_lst.append(data_)

        df_market_data = pd.DataFrame(new_data_lst, columns=columns_lst)
        df_market_data['date'] = pd.to_datetime(df_market_data['date'])
        df_market_data.set_index(['date'], inplace=True)
        return df_market_data

    def get_my_balance(self):
        result = self.accountAPI.get_account('USDT')
        data = result.get('data')[0].get('details')[0]
        mybalance = data.get('availEq')
        return float(mybalance)

    def _get_ticker(self, instId):
        result = self.marketAPI.get_ticker(instId)
        instId_detail = result.get('data')[0]
        return instId_detail

    def cancel_algo_order_(self, algoID, instId):
        """ 撤销委托单 """
        if not algoID:
            algoID = self.get_algoid_data()
        if not algoID:
            return False
        result = self.tradeAPI.cancel_algo_order([{'algoId': algoID, 'instId': instId}])
        algoId, sCode, sMsg = self.check_order_result_data(result, 'algoId')
        return algoId

    def get_algoid_data(self, ordType='oco'):
        """ 获取未完成策略委托单 """
        result = self.tradeAPI.order_algos_list(ordType, instType='SWAP')
        data = result.get('data')
        if not data:
            algoID = False
        else:
            algoID = True
            for item in data:
                algoID = item.get("algoId")
        return algoID
