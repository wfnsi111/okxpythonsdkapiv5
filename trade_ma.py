import pandas as pd
from okx_strategy.MaTrade import drow_k
now_price = ''

file_path = './history_data/history_1H.csv'
df = pd.read_csv(file_path, sep=',', parse_dates=['time'])
df['time'] = pd.to_datetime(df['time'], unit='ms')
df.set_index(['time'], inplace=True)
df['MA5'] = df['close'].rolling(5).mean()
df['MA10'] = df['close'].rolling(10).mean()
print(df.head())
drow_k(df)