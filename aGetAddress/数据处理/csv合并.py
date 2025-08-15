import os
import pandas as pd

# 定义存放CSV文件的文件夹路径
folder_path = '数据'  # 替换为你的CSV文件夹路径

# 获取文件夹中所有CSV文件的文件名
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 初始化一个空的DataFrame来存放合并后的数据
combined_df = pd.DataFrame()

# 逐个读取CSV文件并合并
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    combined_df = pd.concat([combined_df, df], ignore_index=True)

# 筛选出GCJ_02列为0的数据
# filtered_df = combined_df[combined_df['GCJ_lng'] == 0]
filtered_df_finish = combined_df[combined_df['GCJ_lng'] != 0]
# 将筛选后的数据另存为一个新的CSV文件
output_file_path1 = 'filtered_df_finish.csv'  # 替换为你想要保存的文件路径
# output_file_path2 = 'filtered_data.csv'  # 替换为你想要保存的文件路径
combined_df.to_csv(output_file_path1, index=False)
# filtered_df.to_csv(output_file_path2, index=False)

# print(f"筛选后的数据已保存到 {output_file_path}")
