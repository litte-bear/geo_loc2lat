
import json
import time

import pandas as pd
import requests
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
# key = "替换为你的key"  # 替换成你的API key
tk = ["98a4caa1f93b47536b946cd9f4d0aa6c"]  # 替换成你的API key
# http://api.tianditu.gov.cn/v2/search?
# postStr={"keyWord":"学校",
# "polygon":"118.93232636500011,27.423305726000024,118.93146426300007,27.30976105800005,118.80356153600007,27.311829507000027,118.80469010700006,27.311829508000073,118.8046900920001,27.32381604300008,118.77984777400002,27.32381601800006,118.77984779100007,27.312213007000025,118.76792266100006,27.31240586100006,118.76680145600005,27.429347074000077,118.93232636500011,27.423305726000024","queryType":10,"start":0,"count":10}
# &type=query&tk=您的密钥
def get_location_name(location):
    postStr = {
        "tk": tk,
        "location": location,
        "output": "json",
        "batch": 'true'
    }
    url = "http://api.tianditu.gov.cn/v2/search?"
    # response = requests.get(url, parameters)
    session.keep_alive = False
    response = session.get(url, params=postStr)
    data = json.loads(response.text)
    if data["status"] == "1":
        return data['regeocodes']
    else:
        return

# res = session.get('http://api.tianditu.gov.cn/v2/search?postStr={"keyWord":"公园","level":12,"queryRadius":5000,"pointLonlat":"116.48016,39.93136","queryType":3,"start":0,"count":10,"show":2}&type=query&tk=98a4caa1f93b47536b946cd9f4d0aa6c')
# 156320500
res = session.get('http://api.tianditu.gov.cn/v2/search?postStr={"keyWord":"公园","queryType":12,"dataTypes":"180304","show":"2","start":0,"count":10,"specify":"156320500"}&type=query&tk=98a4caa1f93b47536b946cd9f4d0aa6c')
data = json.loads(res.text)
print(data)