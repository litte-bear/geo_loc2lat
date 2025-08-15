import csv
import time

import requests
import lxml
import json
from datetime import datetime


def get_data(timestamp,pagenum):
    url = 'https://zwfw.mca.gov.cn/webglbiz/interface/test/InterfaceToSjyy'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
    stringParams={"access_key":"jmgc_yl","timestamp": timestamp,"biz_content":{"axbe0003":"","axbe0023":"360000000000","pageNumber":pagenum,"pageSize":10},"url":"https://zwxt.mca.gov.cn/fwjc_engine_int/rest/jmgc_yl_queryRecord","method":"post","sign":"","request_id":"","version":"1.0","format":"json"}
    data={
            "stringParams":stringParams,
            "nvc": '1',
            "checkCode":'',
        }
    res = requests.post(url,json=data)
    # print(res.text)
    text=res.text
    # print(text)
    text_json = json.loads(text)
    content = text_json['data']['data']['content']
    content_json = json.loads(content)
    # print(content_json)

    if 'msg' in content_json and 'code' in content_json:
        msg = content_json['msg']
        code = content_json['code']
        if msg == "运行错误" and code == "-300":
            # 重新发送请求
            print("服务器返回错误，正在重新发送请求...")
            return get_data(timestamp, pagenum)
        else:
            list = content_json['biz_data']['data']['pageBean']['list']
            total = content_json['biz_data']['data']['pageBean']['total']
            pageSize = content_json['biz_data']['data']['pageBean']['pageSize']
            # print('数据总量：{0},总共{1}页'.format(total, pageSize))
            return list


def timestamp_gen():
    # 获取当前时间
    current_time = datetime.now()

    # 将当前时间转换为时间戳
    timestamp = int(current_time.timestamp())*1000
    # print("当前时间：", current_time)
    # print("时间戳：", timestamp)
    return timestamp

for i in range(180):
    i = i+1
    timestamp = timestamp_gen()
    data_list = get_data(timestamp, i)
    # 设置CSV文件的基础路径和基础文件名
    csv_base_path = 'data/data'
    # 指定要保存的列名
    fieldnames = ['axbe0004', 'axbe0002', 'axbe0013', 'areaCode', 'axbe0003', 'axbe0023', 'axbe0031',"ahae2347","ahae2323","ahae2343"]

    # 生成当前保存的CSV文件路径
    csv_file_path = f"{csv_base_path}{i}.csv"

    # 将数据写入CSV文件
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data_list:
            writer.writerow({key: row[key] for key in fieldnames})

    print("CSV文件已生成：", csv_file_path)

    time.sleep(2)

    print('当前查询第{}页'.format(i))
