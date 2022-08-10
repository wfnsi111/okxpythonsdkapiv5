# -*- coding: utf-8 -*-

from Mylog.mylog import LoggerHandler
import time
import okx.Account_api as Account
import okx.Trade_api as Trade
import okx.Market_api as Market
import okx.Funding_api as Funding
import okx.Public_api as Public
import okx.status_api as Status
import okx.subAccount_api as SubAccount
import okx.TradingData_api as TradingData
import okx.Broker_api as Broker
import okx.Convert_api as Convert
import okx.FDBroker_api as FDBroker
import okx.Rfq_api as Rfq
import okx.TradingBot_api as TradingBot
import pandas as pd
import datetime
import re
from basetrade.basedb import BaseDb
from basetrade.accountinfo import AccountInfo
import json


class BaseTrade(BaseDb):
    def __init__(self, api_key, secret_key, passphrase, use_server_time=False, flag='1'):
        super().__init__()
        self.marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, use_server_time, flag)
        self.accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, use_server_time, flag)
        self.tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, use_server_time, flag)
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
        self.account_obj_lst = []
        self.account_obj_lst_error = []

    def timestamp_to_date(self, t):
        # 13位时间戳转日期
        timestamp = float(t)/1000
        timearray = time.localtime(timestamp)
        date = time.strftime("%Y-%m-%d %H:%M:%S", timearray)
        return date



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

    def _get_market_data(self, instId, bar, ma_lst=None, vol_ma=None, limit='100'):
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

        df = pd.DataFrame(new_data_lst, columns=columns_lst)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        if isinstance(ma_lst, list):
            for ma in ma_lst:
                ma_num = int(re.findall(r"\d+", ma)[0])
                df[ma] = df['close'].rolling(ma_num).mean()
        if vol_ma:
            # vol_ma_num = int(re.findall(r"\d+", vol_ma)[0])
            df['vol_ma'] = df['volume'].rolling(vol_ma).mean()
        return df

    def _get_candle_data(self, instId, bar, ma_lst=None, vol_ma=None, limit='100'):
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

        df = pd.DataFrame(new_data_lst, columns=columns_lst)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index(['date'], inplace=True)
        if isinstance(ma_lst, list):
            for ma in ma_lst:
                ma_num = int(re.findall(r"\d+", ma)[0])
                df[ma] = df['close'].rolling(ma_num).mean()
        if vol_ma:
            # vol_ma_num = int(re.findall(r"\d+", vol_ma)[0])
            df['vol_ma'] = df['volume'].rolling(vol_ma).mean()
        return df

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

    def get_timestamp(self):
        now = datetime.datetime.now()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"

    def get_order_details(self, instId, ordId=''):
        result = self.tradeAPI.get_orders(instId, ordId)
        self.order_details = result.get('data')[0]
        avgPx = self.order_details.get('avgPx')
        state = self.order_details.get('state')
        side = self.order_details.get('side')
        pnl = self.order_details.get('pnl')
        # state = self.order_details.get('state')
        msg = '%s 开仓成功，均价：%s, 状态：%s, 方向：%s' % (instId, avgPx, state, side)
        self.log.info(msg)
        return self.order_details

    def currency_to_sz(self, instId, currency):
        """ 币转张 """
        coefficient = 1
        if 'ETH' in instId:
            coefficient = 10
        elif 'DOG' in instId:
            coefficient = 1000
        elif 'BTC' in instId:
            coefficient = 100
        sz = currency * coefficient
        return sz

    def set_initialization_account(self, instId, lever='10', mgnMode='cross'):
        """ 初始化账户 """
        obj_lst = self.get_account_obj()
        # l = len(obj_lst)
        i = 1
        for index, obj in enumerate(obj_lst):
            print("\r"+"信息加载中" + '.' * i + ' ' * (7 - i), flush=True, end='')
            i += 1
            if i == 7:
                i = 1
            time.sleep(0.2)
            try:
                mybalance, frozenBal = obj.get_my_balance()
                if frozenBal != '0' and frozenBal:
                    # 不为空， 则有持仓
                    obj.status = 'trading'
                    sql = """ UPDATE %s SET status='%s' where api_key='%s' """ % (self.account_table, obj.status, obj.api_key)
                else:
                    obj.balance = mybalance
                    result = obj.accountAPI.get_position_mode('long_short_mode')
                    result = obj.accountAPI.set_leverage(instId=instId, lever=lever, mgnMode=mgnMode)
                    obj.status = 'free'
                    sql = """ UPDATE %s SET balance='%s',status='%s'  where api_key='%s' """ % (self.account_table, mybalance, obj.status, obj.api_key)
                result = self.db_update(sql)
                if not result:
                    self.log.error('initialization account error: api_key: %s' % obj.api_key)
                    continue
                self.account_obj_lst.append(obj)
            except Exception as e:
                obj.status = 'error'
                obj.msg.append(e)
                sql = """ UPDATE %s set status='%s', msg='[%s]'  where api_key='%s' """ % (self.account_table, obj.status, e, obj.api_key)
                result = self.db_update(sql)
                self.log.error('initialization account error: api_key: %s, %s' % (obj.api_key, e))
                self.account_obj_lst_error.append(obj)

    def get_account_obj(self):
        # sql_where1 = """ status = 'free' """
        # sql_where2 = """ flag = '1' """
        sql_where3 = """ operate = '1' """
        sql_where = 'and'.join([sql_where3])
        sql = """ select api_key, secret_key, passphrase, status, flag from %s where %s """ % (self.account_table, sql_where)
        res = self.db_query(sql)
        if not res:
            self.log.error('No operate Account Info!!!')
            raise
        obj_lst = []
        for item in res:
            account_obj = AccountInfo(item[0], item[1], item[2], item[3], flag=item[4])
            obj_lst.append(account_obj)
        return obj_lst

    def update_account_status(self, account_obj, status):
        msg = json.dumps(account_obj.msg)
        sql = """ UPDATE %s SET status='%s', msg='%s' where api_key='%s' """ % (self.account_table, status, msg, account_obj.api_key)

        result = self.db_update(sql)

