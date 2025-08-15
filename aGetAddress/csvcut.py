# %%
import pandas as pd
import warnings

warnings.filterwarnings("ignore")
import os

os.chdir('datacut')

# %%

# 设置大CSV文件路径
# large_csv_file = '../待匹配地址(含市县信息).csv'
large_csv_file = './info_2.csv'

# 设置每个小CSV文件的行数
chunk_size = 75000

# 初始化文件编号
file_number = 1

# 读取大CSV文件并分割为小CSV文件
chunks = pd.read_csv(large_csv_file, chunksize=chunk_size)

for chunk in chunks:
    try:
        # 构造小CSV文件名
        small_csv_file = f'info_2{file_number}.csv'

        # 将数据写入小CSV文件
        chunk.to_csv(small_csv_file, index=False)

        file_number += 1
    except UnicodeDecodeError:
        print("UnicodeDecodeError: Skipping problematic chunk")

# 处理最后一个数据块，如果行数不足1000000
if len(chunk) < chunk_size:
    try:
        small_csv_file = f'info_2{file_number}.csv'
        chunk.to_csv(small_csv_file, index=False)
    except UnicodeDecodeError:
        print("UnicodeDecodeError: Skipping the last problematic chunk")