# -*- coding: utf-8 -*-

"""
高点：  大于前4，大于后4，
低点：  小于前4，小于于后4，


"""

import pandas as pd
import mplfinance as mpf
import time
from basetrade.basetrade import BaseTrade
import json
import asyncio
import websockets
import datetime


class BoxStrategy(BaseTrade):
    def __init__(self, api_key=None, secret_key=None, passphrase=None, use_server_time=False, flag='1', **kwargs):
        super().__init__(api_key, secret_key, passphrase, use_server_time, flag)
        self.df = None
        self.stop_loss = 0
        self.ma = kwargs.get('ma' '')
        self.instId = kwargs.get('instId')
        self.bar1 = kwargs.get('bar1')
        self.bar2 = kwargs.get('bar2', '1D')
        self.candle_count = 4
        self.last_high = 0
        self.last_low = 0
        self.df = None

    def start_my_trade(self):
        atr = self.get_atr_by_bar2(self.bar2)
        df = self.get_market_by_bar1(self.bar1)
        url = "wss://ws.okx.com:8443/ws/v5/public"
        # 行情频道
        # channels = [{"channel": "tickers", "instId": self.instId}]
        # K线频道
        channels = [{"channel": "candle5m", "instId": self.instId}, {"channel": "candle15m", "instId": self.instId},
                    {"channel": "candle30m", "instId": self.instId}, {"channel": "candle1m", "instId": self.instId}]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.subscribe_without_login(url, channels, df))
        print('OK')

    def get_atr_by_bar2(self, bar, limit=14):
        self.df = self._get_market_data(self.instId, bar, limit=limit)
        atr = self.get_atr_data(self.df, limit)
        return atr

    def get_market_by_bar1(self, bar, limit='100'):
        df = self._get_market_data(self.instId, bar, limit=limit, set_index=False)
        l = df.shape[0]
        last_high_index = 0
        last_low_index = 0
        min_low = 0
        if l > 2 * self.candle_count + 1:
            # df['max'] = df.rolling(9).max()
            for i in range(self.candle_count, l - self.candle_count - 1):
                tar_high = df.loc[i, 'high']
                tar_low = df.loc[i, 'low']
                if tar_high >= df.loc[i-1, 'high'] and tar_high >= df.loc[i-2, 'high'] \
                        and tar_high >= df.loc[i-3, 'high'] and tar_high >= df.loc[i-4, 'high']:
                    if tar_high >= df.loc[i+1, 'high'] and tar_high >= df.loc[i+2, 'high'] \
                            and tar_high >= df.loc[i+3, 'high'] and tar_high >= df.loc[i+4, 'high']:
                        df.at[i, 'max'] = tar_high
                        last_high_index = i
                        self.last_high = tar_high

                if tar_low <= df.loc[i-1, 'low'] and tar_low <= df.loc[i-2, 'low'] \
                        and tar_low <= df.loc[i-3, 'low'] and tar_low <= df.loc[i-4, 'low']:
                    if tar_low <= df.loc[i+1, 'low'] and tar_low <= df.loc[i+2, 'low'] \
                            and tar_low <= df.loc[i+3, 'low'] and tar_low <= df.loc[i+4, 'low']:
                        df.at[i, 'min'] = tar_low
                        last_low_index = i
                        self.last_low = tar_low
        return df

    async def subscribe_without_login(self, url, channels, df):
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

                        print(self.get_timestamp() + res)
                        res = eval(res)
                        #  60018   频道不存在
                        if 'event' in res:
                            continue
                        # data = res.get('data')[0]
                        # date = self.timestamp_to_date(data[0])
                        # last = data[4]
                        # time.sleep(3)
                        # if last >= self.last_high:
                        #     print('sell')
                        # if last <= self.last_low:
                        #     print('buy')

            except Exception as e:
                print(e)
                print("连接断开，正在重连……")
                continue

    def get_timestamp(self):
        now = datetime.datetime.now()
        t = now.isoformat("T", "milliseconds")
        return t + "Z"