# 获取交易产品历史K线数据（仅主流币实盘数据）  Get Candlesticks History（top currencies in real-trading only）
# 历史数据最多只能获取100条

import okx.Market_api as Market
import time
import json
import csv
import datetime
import os

api_key = "e20364fd-ad1a-4528-b1b2-9c5151438ec5"
secret_key = "8DF8C22076B835D80A21E48EE5BBF301"
passphrase = "Kangkang1_"
# flag = '1'  # 模拟盘 demo trading
flag = '0'  # 实盘 real trading

def get_time(t, bar):
    # 当前日期
    t1 = t.strftime('%Y-%m-%d %H:%M:%S')
    # 转为秒级时间戳
    ts1 = time.mktime(time.strptime(t1, '%Y-%m-%d %H:%M:%S'))
    # 转为毫秒级
    end_time = int(str(ts1 * 1000).split(".")[0])
    bar_num = int(bar.strip('mHDW')) * 100
    akey = {}
    if 'D' in bar:
        akey = {'days': bar_num}
    elif 'W' in bar:
        akey = {'weeks': bar_num}
    elif 'm' in bar:
        akey = {'minutes': bar_num}
    elif 'h' in bar:
        akey = {'hours': bar_num}
    # cls, days=0, seconds=0, microseconds=0,
    #                 milliseconds=0, minutes=0, hours=0, weeks=0):
    t3 = t - datetime.timedelta(**akey)
    t2 = t3.strftime("%Y-%m-%d %H:%M:%S")
    # 转为秒级时间戳
    ts2 = time.mktime(time.strptime(t2, '%Y-%m-%d %H:%M:%S'))
    # 转为毫秒级
    start_time = int(str(ts2 * 1000).split(".")[0])
    # print("\n", "*" * 30)
    #
    # print(start_time)
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts2)))
    #
    # print("*" * 30)
    #
    # print(end_time)
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts1)))
    #
    # print("*" * 30, "\n")
    return end_time, start_time, t3


def delete_data(f_path):
    if os.path.exists(f_path):
        os.remove(f_path)
        print('删除原来的历史数据')

def data_to_save(bar):
    f_path = "./history_data/history_%s.csv" % bar
    delete_data(f_path)
    with open(f_path, "a", newline='') as csvfile:
        # get_history_candlesticks(self, instId, after='', before='', bar='', limit=''):
        # loop_times = 4
        loop_times = 1
        time_end = datetime.datetime.now()
        for i in range(loop_times):
            after, before, time_end = get_time(time_end, bar)
            #  时间戳长度为13 毫秒级
            after = ''
            before = ''
            print(after, before, bar)
            marketAPI = Market.MarketAPI(api_key, secret_key, passphrase, True, flag)
            result = marketAPI.get_history_candlesticks('BTC-USDT-SWAP', after=after, before=before, bar=bar, limit='100')
            print(len(result['data']))
            # data_to_save(result, i)
            # print(print(json.dumps(result)))
            writer = csv.writer(csvfile)
            data = result.get("data")
            columns_name = ['time', 'open', 'high', 'low', 'close', 'volume', 'volCcy']
            if i == 0:
                writer.writerow(columns_name)
            lenth = len((result['data']))
            for item in range(lenth, 0, -1):
                # 转换成localtime
                dataList = data[item-1]
                ts = float(dataList[0])/1000
                time_local = time.localtime(ts)
                # 转换成新的时间格式(2016-05-05 20:28:54)
                dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
                dataList[0] = dt
                writer.writerow(dataList)
    print('更新历史数据完成')


if __name__ == '__main__':
    bar = '1H'
    # bar = '3m'

    data_to_save(bar)