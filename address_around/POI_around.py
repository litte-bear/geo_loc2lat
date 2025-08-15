import json
import time
import Levenshtein
import pandas as pd
import requests

key = "96126dfd866a1563aab102157956c49a"  # 替换成你的API key


# key = "替换成你的API key"  # 替换成你的API key

def get_location_name(location):
    parameters = {
        "key": key,
        "location": location,
        "output": "json",
        "batch": 'true',
        "poitype": "090100|090200|141200|150500",
        "radius": "1000",
        "extensions": "all"
    }
    url = "https://restapi.amap.com/v3/geocode/regeo"
    response = requests.get(url, parameters)
    data = json.loads(response.text)
    if data["status"] == "1":
        print(data)
        return data['regeocodes']
    else:
        return None


file_path = 'data.xlsx'
df = pd.read_excel(file_path)
df = pd.DataFrame(df)
lng = df['百度经度'].to_numpy()
lat = df['百度纬度'].to_numpy()
locations = [[lng[i], lat[i]] for i in range(len(lng))]

# print(locations)
# test_location = [[116.362, 39.8784]]
# test_location = [[116.362, 39.8784],[116.417, 39.9289]]

coordinates = locations
# 将原始坐标点数组划分为每20个点为一组的子组
group_size = 20
coordinate_groups = [coordinates[i:i + group_size] for i in range(0, len(coordinates), group_size)]

# 将每个子组内的点转换为指定格式的字符串，并用'|'分隔不同点的字符串
formatted_coordinates = ['|'.join([f'{point[0]},{point[1]}' for point in group]) for group in coordinate_groups]
# print(formatted_coordinates[0])
data = []
# for group in formatted_coordinates:
#     data_20 = get_location_name(group)
#     data.append(data_20)
#     print('查询中。。。')
for i, group in enumerate(formatted_coordinates):
    if i % 100 == 0 and i > 0:
        print(f'已查询{i}组数据，休息120秒...')
        time.sleep(120)
    data_20 = get_location_name(group)
    data.append(data_20)
    print(f'查询逆地理编码中（进度：{i + 1}/{len(formatted_coordinates)}）...')
print('逆地理编码查询完成')
# print(data[0])
merged_data = [item for sublist in data for item in sublist]
# print(merged_data[0])

for i in range(len(merged_data)):
    adata = merged_data
    if bool(adata[i]["addressComponent"]['businessAreas']):
        businessAres = len(adata[i]["addressComponent"]['businessAreas'])
    else:
        businessAres = 0
    # 初始化计数变量
    subway_count = 0
    hospital_count = 0
    processed_hospitals = set()
    school_count = 0


    # 定义一个函数来检查医院名称是否相似

    def is_similar(name1, name2):
        # 使用Levenshtein距离来衡量字符串相似性
        distance = Levenshtein.distance(name1, name2)
        # 如果距离小于某个阈值，可以认为两个字符串相似
        similarity_threshold = 10  # 根据实际情况调整阈值
        return distance <= similarity_threshold


    # 遍历数据并判断'type'字段
    for item in adata[i]['pois']:
        poi_type = item['type']
        if '地铁站' in poi_type:
            subway_count += 1
        if '医疗保健服务' in poi_type:
            # 获取医院名称
            hospital_name = item['name']
            # 遍历已处理的医院名称，检查是否与当前医院名称相似
            is_duplicate = False
            for processed_hospital in processed_hospitals:
                if is_similar(hospital_name, processed_hospital):
                    is_duplicate = True
                    break
            # 如果当前医院名称不与已处理的医院相似，增加医院数量并将其添加到字典
            if not is_duplicate:
                hospital_count += 1
                processed_hospitals.add(hospital_name)
        if '学校' in poi_type:
            school_count += 1
    df.loc[i, '周边（500m或1km）是否有商圈'] = businessAres
    df.loc[i, '周边（500m或1km）是否有地铁站'] = subway_count
    df.loc[i, '周边（500m或1km）是否有医院'] = hospital_count
    df.loc[i, '周边（500m或1km）是否有学校'] = school_count

    # province = adata[i]['addressComponent']['province']
    # city = adata[i]['addressComponent']['city']
    # district = adata[i]['addressComponent']['district']
    # # 去除和'province'、'district'、'city'相同的字段
    # formatted_address = adata[i]['formatted_address'].replace(
    #     province, '')
    # if bool(district) == True:
    #     formatted_address = formatted_address.replace(district, '')
    # if bool(city)==True:
    #     formatted_address = formatted_address.replace(city, '')
    #
    # # 移除字符串开头和结尾的空格
    # formatted_address = formatted_address.strip()
    #
    # # df.loc[i, '所在省'] = province
    # #
    # # if not city:
    # #     df.loc[i, '所在市'] = province
    # # else:
    # #     df.loc[i, '所在市'] = city
    # #
    # # if not district:
    # #     district = ' '
    # # else:
    # #     df.loc[i, '所在区县'] = district
    # df.loc[i, '街道'] = formatted_address
    print(i)
    print(f'保存中（进度：{i + 1}/{len(merged_data)}）...')

# 将 DataFrame 保存为 Excel 文件
df.to_excel('output_file.xlsx', index=False)
