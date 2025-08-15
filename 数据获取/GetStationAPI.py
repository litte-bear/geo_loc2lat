import os
import pandas as pd
# 指定目录路径
import requests
import json
from requests.packages.urllib3.util.retry import Retry

# 创建一个自定义的重试策略
retry_strategy = Retry(
    total=10,  # 最大重试次数
    status_forcelist=[429, 500, 502, 503, 504, 10060],  # 需要重试的状态码
    backoff_factor=1  # 重试间隔的因子
)

# 创建一个 Session 对象，并将重试策略应用于该 Session
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
session.mount('https://', adapter)



def getStationLocation(file_path):
    # # 获取目录下所有文件
    # files = [f for f in os.listdir(directory_path) if f.endswith('.xlsx') or f.endswith('.xls')]
    # # 遍历每个文件
    #
    #
    # for file in files:
    #     file_path = os.path.join(directory_path, file)

    # 读取 Excel 文件
    df = pd.read_excel(file_path)

    # 获取前三列数据
    locations = df.iloc[:, 1:3].values.tolist()
    print(locations)
    print("---获取到车站GPS数据---")
    return locations

def getPOI(locations):
    """
    获取POI信息
    :type locations: 公交车站经纬度
    """
    type_dict = {
        "consumer":"050000|060000", ## 消费服务: 包含餐饮、购物；
        "medical":"080000|090000", ## 医疗休闲：包含体育场所、医院等；
        "residence":"100000|120000", ##住宅住宿:包含小区、宾馆等；
        "school":"140000", ## 科教场所包含学校、博物馆等
        "office":"130000|170000", ## 包含政府、企业等办公区域
        "transport":"150000", ## 包含火车站、地铁站等
    }
    result_list = [] ##存储所有
    for index,location in enumerate(locations):
        print(index)
        result = dict()
        result['Longitude'] = str(location[0])
        result['Latitude'] = str(location[1])
        for type,code in type_dict.items():
            type_num = 0
            page_size_current = 0
            page_num = 1
            while page_size_current == '25' or page_num == 1 : ##统计数量，大于一页的数量便翻页
                session.keep_alive = False
                info = session.get("https://restapi.amap.com/v5/place/around?parameters",params={
                    "key":"69a6a5059540f2696762b62de45c8533",
                    "types":code,
                    "location": result['Longitude'] + "," + result['Latitude'],
                    "radius":"200",
                    "page_size":"25",
                    "page_num": page_num
        })
                info_dict = json.loads(info.text)
                page_size_current = info_dict['count']
                type_num += int(page_size_current)
                page_num += 1
            result[type] = str(type_num)
        result_list.append(result)
    print("---获取到车站POI数据---")
    return result_list

# def getSationStopType(locations):
#     """
#     获取公交车站类型，和是否有上下客区域
#     :param locations:
#     """
#     type_dict = {
#         "all":"150700" ## 普通公交站
#     }
#     result_list = []
#     for index,location in enumerate(locations):
#         result = dict()
#         result['Longitude'] = str(location[0])
#         result['Latitude'] = str(location[1])
#         type_num = 0
#         info = requests.get("https://restapi.amap.com/v5/place/around?parameters",params={
#             "key":"ec86bd4112ecc1399c5e80cdd7fb6bc5",
#             "types":"150700",
#             "location":result['Longitude']+","+result['Latitude'],
#             "radius":"100",
#             "page_size":"25"
#             # "page_num": page_num
#         })
#         info_dict = json.loads(info.text)
#         buses = set()
#         for poi in info_dict['pois']:
#             address = poi['address'].split(";")
#             buses.update(address)
#         result['bus_line'] = str(len(buses))
#         result['bus_staion'] = str(len(info_dict['pois']))
#         result_list.append(result)
#     print("---获取到车站类型数据---")
#     return result_list
def writeToExcel(file_path,result_list):
    """
    写入信息
    :param file_path:
    :param result_list:
    :param start_index:
    """
    df = pd.DataFrame(result_list,dtype=str)
    print(df)
    df_orrigin= pd.read_excel(file_path,dtype=str)
    print(df_orrigin)
    df_combined = pd.merge(df,df_orrigin)
    # 读取现有的 Excel 文件或创建一个新的
    with pd.ExcelWriter(file_path,engine="openpyxl") as writer:
        df_combined.to_excel(writer,index=False,header=True)
    print("---车站数据写入成功---")
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_path = r'bus stop/873路(美茵河谷--江南体育馆).xlsx'
    locations = getStationLocation(file_path) #获取坐标；
    result_list = getPOI(locations) #获取要写入的信息
    print(result_list)
    writeToExcel(file_path,result_list) #写入excel