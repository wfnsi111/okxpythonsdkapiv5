import re
bar = '15min'
import time



t_inv = int(re.findall(r"\d+", bar)[0]) * 3
for i in range(t_inv):

    print(i)
    time.sleep(1)