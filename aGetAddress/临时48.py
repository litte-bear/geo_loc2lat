import requests
import json
import chardet
import math
key = '4ee25368882822d485fc6c5bc27bc13b'  # 高德申请的key
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
path = r"C:\Users\zhang qian\Desktop\POI_data\data\1、处理空间"  # 处理数据的路径
file1 = r"\位置提取_test.csv"  # 需要读取的文件

file2 = r"\位置提取_test result.csv"  # 需要生成和保存的文件
error_file1 = r'\error1.csv'  # 爬取失败保存的记录文件
error_file2 = r'\error2.csv'  # 解析失败保存的记录文件
def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)
def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [round(lng * 2 - mglng, 6), round(lat * 2 - mglat, 6)]

def get_url(url):  # 发送请求返回文本
    r = requests.get(url, timeout=5)

    #     r.encoding = 'utf-8'
    rr = r.text
    print(rr)
    return rr


def parse_url(t, f, address):  # 解析文本
    global lon_lat_gcj02, xy_gcj02, xy_wgs, xy_detail
    js = json.loads(t)
    lon_lat_gcj02 = js['geocodes'][0]['location']
    xy_gcj02 = lon_lat_gcj02.split(',')
    xy_gcj02[0] = float(xy_gcj02[0])
    xy_gcj02[1] = float(xy_gcj02[1])
    xy_wgs = gcj02_to_wgs84(xy_gcj02[0], xy_gcj02[1])  # 火星坐标转WGS84坐标
    xy_detail = xy_gcj02 + xy_wgs
    for i in range(len(xy_detail)):
        xy_detail[i] = str(xy_detail[i])
    print(address + ',' + ','.join(xy_detail))
    f.write(address + ',' + ','.join(xy_detail) + '\n')


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']


def main():
    global url, t, f2
    with open(path + file1, 'r', encoding='GB2312', errors='ignore') as f1, \
            open(path + file2, 'w+', encoding='utf-8', errors='ignore') as f2, \
            open(path + error_file1, 'w+', encoding='utf-8', errors='ignore') as f3, \
            open(path + error_file2, 'w+', encoding='utf-8', errors='ignore') as f4:
        global line1
        line1 = f1.readline()
        f2.write(line1.strip() + ",高德X,高德Y,WGS84(X),WGS84(Y)\n")  # 字段开头
        line1 = f1.readline()
        while bool(line1):
            line1_ls = line1.strip().split(",")
            address = line1_ls[-1]
            url = "https://restapi.amap.com/v3/geocode/geo?" + "address=" + address + "&key=" + key  # url构造
            print(url)
            try:
                t = get_url(url)
            except:
                print(line1.strip() + ",网页爬取失败")  # 异常处理
                f3.write(line1)
                line1 = f1.readline()
                continue
            try:

                parse_url(t, f2, line1.strip())
            except:
                print(line1.strip() + ",网页解析失败")  # 异常处理
                f4.write(line1)
                line1 = f1.readline()
                continue
            line1 = f1.readline()


if __name__ == '__main__':
    main()