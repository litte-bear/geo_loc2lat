import threading
import json
import pandas as pd
import requests
from requests.packages.urllib3.util.retry import Retry
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
PI = math.pi
PIX = math.pi * 3000 / 180
EE = 0.00669342162296594323
A = 6378245.0


def bd09_to_gcj02(lng, lat):
    """BD09 -> GCJ02"""
    x, y =  lng - 0.0065, lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * PIX)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PIX)
    lng, lat = z * math.cos(theta), z * math.sin(theta)
    return lng, lat


def gcj02_to_bd09(lng, lat):
    """GCJ02 -> BD09"""
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * PIX)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * PIX)
    lng, lat = z * math.cos(theta) + 0.0065, z * math.sin(theta) + 0.006
    return lng, lat


def gcj02_to_wgs84(lng, lat):
    """GCJ02 -> WGS84"""
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    lng, lat = lng - dlng, lat - dlat
    return lng, lat


def wgs84_to_gcj02(lng, lat):
    """WGS84 -> GCJ02"""
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (A / sqrtmagic * math.cos(radlat) * PI)
    lng, lat = lng + dlng, lat + dlat
    return lng, lat


def mapbar_to_wgs84(lng, lat):
    """MapBar -> WGS84"""
    lng = lng * 100000.0 % 36000000
    lat = lat * 100000.0 % 36000000
    lng1 = int(lng - math.cos(lat / 100000.0) * lng / 18000.0 - math.sin(lng / 100000.0) * lat / 9000.0)
    lat1 = int(lat - math.sin(lat / 100000.0) * lng / 18000.0 - math.cos(lng / 100000.0) * lat / 9000.0)
    lng2 = int(lng - math.cos(lat1 / 100000.0) * lng1 / 18000.0 - math.sin(lng1 / 100000.0) * lat1 / 9000.0 + (1 if lng > 0 else -1))
    lat2 = int(lat - math.sin(lat1 / 100000.0) * lng1 / 18000.0 - math.cos(lng1 / 100000.0) * lat1 / 9000.0 + (1 if lat > 0 else -1))
    lng, lat = lng2 / 100000.0, lat2 / 100000.0
    return lng, lat


def transform_lat(lng, lat):
    """GCJ02 latitude transformation"""
    ret = -100 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * PI) + 40.0 * math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * PI) + 320.0 * math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transform_lng(lng, lat):
    """GCJ02 longtitude transformation"""
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * PI) + 20.0 * math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * PI) + 40.0 * math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * PI) + 300.0 * math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """No offset when coordinate out of China."""
    if lng < 72.004 or lng > 137.8437:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False


def bd09_to_wgs84(lng, lat):
    """BD09 -> WGS84"""
    lng, lat = bd09_to_gcj02(lng, lat)
    lng, lat = gcj02_to_wgs84(lng, lat)
    return lng, lat


def wgs84_to_bd09(lng, lat):
    """WGS84 -> BD09"""
    lng, lat = wgs84_to_gcj02(lng, lat)
    lng, lat = gcj02_to_bd09(lng, lat)
    return lng, lat


def mapbar_to_gcj02(lng, lat):
    """MapBar -> GCJ02"""
    lng, lat = mapbar_to_wgs84(lng, lat)
    lng, lat = wgs84_to_gcj02(lng, lat)
    return lng, lat


def mapbar_to_bd09(lng, lat):
    """MapBar -> BD09"""
    lng, lat = mapbar_to_wgs84(lng, lat)
    lng, lat = wgs84_to_bd09(lng, lat)
    return lng, lat

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
# key = "替换为你的key"  # 替换成你的API key
# key = "69a6a5059540f2696762b62de45c8533"  # 替换成你的API key
key = "96126dfd866a1563aab102157956c49a"  # 替换成你的API key
def get_location_name(location):
    parameters = {
        "key": key,
        "location": location,
        "output": "json",
        "batch": 'true'
    }
    url = "https://restapi.amap.com/v3/geocode/regeo"
    # response = requests.get(url, parameters)
    session.keep_alive = False
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    if data["status"] == "1":
        return data['regeocodes']
    else:
        return None
def GPS_to_Gcj(location):
    parameters = {
        "key": key,
        "locations": location,
        "coordsys": "gps",
        "output": "json"

    }
    url = "https://restapi.amap.com/v3/assistant/coordinate/convert?parameters"
    session.keep_alive = False
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    if data["status"] == "1":
        # print(data)
        return data['locations']
    else:
        return None
def get_location_POI(index,address):
    try:
        parameters = {
            "key": key,
            "address": address,
            # "city": 320583,
            "output": "json",
            "batch": 'true',
            # "extensions": "all",
        }
        url = "	https://restapi.amap.com/v3/geocode/geo?parameters"
        # response = requests.get(url, parameters)
        session.keep_alive = False
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        # print(data)
        if data["status"] == "1":
            # print(data)
            geocodes = data['geocodes']
        else:
            geocodes = None
        if geocodes is not None and len(geocodes) > 0:
            first_geocode = [geocodes[0]]
        else:
            first_geocode = [{'formatted_address': '无', 'location': '0,0'}]
    except Exception as e:
        print(f"请求错误: {e}")
        first_geocode = [{'formatted_address': '无', 'location': '0,0'}]
    data_group[index] = first_geocode
    # print(data_group)



# 需要修改：1、file_path, 2、combined_address, 3、output
file_path = '../数据处理/data.csv'

df = pd.read_csv(file_path)
df = pd.DataFrame(df)

combined_addresses = df["address"].to_numpy()
# citys = df["中国申请人地市"].to_numpy()

data_group = [None]*len(combined_addresses)

max_workers = 10

# 总任务数量
total_tasks = len(combined_addresses)
completed_tasks = 0
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    # 提交所有任务到线程池
    futures = [executor.submit(get_location_POI, i,address) for i,address in enumerate(combined_addresses)]

    # 等待所有任务完成
    for future in tqdm(as_completed(futures),total=len(futures)):
        try:
            result = future.result()
            # 处理每个任务的结果（如果有返回值）
        except Exception as e:
            print(f"任务执行出错: {e}")
        # 更新并显示进度
        completed_tasks += 1
        progress = (completed_tasks / total_tasks) * 100
        # print(f"进度: {completed_tasks}/{total_tasks} ({progress:.2f}%)")
# print(data_group)
merged_data = [item for sublist in data_group for item in sublist]
# print(merged_data)


# print(merged_data)
point = []

for i in tqdm(range(len(merged_data))):
    adata = merged_data
    location = adata[i]["location"]
    # if bool(location)==True and adata[i]["district"]==districts[i]:
    if bool(location)==True :
        # if adata[i]["district"]==districts[i] or districts[i] in adata[i]["formatted_address"]:
        location_list = list(map(float, location.split(',')))
        wgs84 = bd09_to_wgs84(location_list[0], location_list[1])
        df.loc[i,'GCJ_lng'] = location_list[0]
        df.loc[i,'GCJ_lat'] = location_list[1]
        df.loc[i, "WGS84_lng"] = wgs84[0]
        df.loc[i, "WGS84_lat"] = wgs84[1]
        df.loc[i,"解析结果"] = adata[i]["formatted_address"]
        point.append(location_list)
    else:
        # print(location)
        df.loc[i, 'GCJ_lon'] = 0
        df.loc[i, 'GCJ_lat'] = 0
        point.append([0,0])

# df.to_excel('../结果数据/output_file21.xlsx', index=False)
# df.to_csv('../结果数据/output_file21.csv', index=False)
df.to_csv('../结果数据/data-out.csv', index=False)
# df.to_excel('../结果数据/test2.xlsx', index=False)
# df.to_csv('../结果数据/test.csv', index=False)

