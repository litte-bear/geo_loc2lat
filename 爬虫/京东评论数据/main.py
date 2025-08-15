import requests
import json

def get_comments():
    url='https://api.m.jd.com/?appid=item-v3&functionId=pc_club_productPageComments&client=pc&clientVersion=1.0.0&t=1715306250372&body=%7B%22productId%22%3A100017087640%2C%22score%22%3A0%2C%22sortType%22%3A5%2C%22page%22%3A2%2C%22pageSize%22%3A10%2C%22isShadowSku%22%3A0%2C%22rid%22%3A0%2C%22fold%22%3A1%2C%22bbtf%22%3A%22%22%2C%22shield%22%3A%22%22%7D&h5st=20240510095730377%3B965zmgit59y9y597%3Bfb5df%3Btk03wa0ac1c2a18nfwoRQBAQ7RLBKo9URlCI3IXj-hihN8whrpnSNYeyrDK_C-XBzVeHT0ECDiHOgbuufvRJSSFgeN0d%3B20c7606e15c2d8959147bd1b2e2142db188afa010afe7076ce5ab8e54b25c234%3B4.7%3B1715306250377%3BV_yBvVVq1Ahg6UQOAzJKApg8mUmxVDgVm-6A6qPLwcIqyD0-bxurJ9RLsdJBbnV1P2b7gaHmD1qFwrveBJ7lE_P-Av8_LxC9VaMEl5ZyJ2qadXHAq-tBGXhGqcncRZjqL6_Vtj7FrdiSng5cxeoH99BLx0-Dga7LgZRfrn58BxDKAthwHWtI5I4HaCqq2zpfwP2U7k_Sw5NsFO-ColakP1AUhV1g6jyFCzVq_XZXpdnYaiCvWemVwXtbkjfbuGogpKg1QqLl8uLIIo7jEQFEiMU279FuniRfvOysRxoWyS8LDMVntdQzQeSx9RopGEdhgEKqnfaj7Xq0cY51vi4EMi0hI_D104cxDABIeMdghdlmqrl6-3Fgxzct4K5nkEA5gFRNxjNydFnwm9U7yPcQcxaS8dAsALedKeW74EF8TiNwhnNGxWpj4l3uesAyixfBPP4bq-O7RwkFuR9LvZ9SvghbsHQ3rmr7YbzMCxsEjT0WEOjrYhoXf5zlqnyV8bga7r1yPpnU5fpvuRD51Y6Pj-wkAJFNt3qaXd56MVA-oTA5ggE7nDk8PeheJO0dl8zjLad9Prk3hGJ0DQIeqffFGvzEemLTD52YgeDqWQHLXbk3&x-api-eid-token=jdd03LXEZUIBXOPD5LT4RWBLWJWKZLOTZMBSZJPD7ZGFJHV4JPIGPWDYAH5EES6AYSNSJE7KBCQF2PFWKC2QVOXGB5Y2IIUAAAAMPMA3XHRIAAAAACROYORVEA7PMKYX&loginType=3&uuid=181111935.1709618170110915536586.1709618170.1715247364.1715306198.3'
    res = requests.get(url)
    print(res.text)
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_comments()


