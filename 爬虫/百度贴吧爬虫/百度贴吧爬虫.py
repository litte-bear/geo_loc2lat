from lxml import etree
import requests


index_url = "https://tieba.baidu.com/p/5475267611"

response = requests.get(index_url).text

selector = etree.HTML(response)

img_list = selector.xpath('//img[@class="BDE_Image"]/@src')

offset = 0

for img_url in img_list:
    img_content = requests.get(img_url).content
    with open('{}.jpg'.format(offset),'wb') as f:
        f.write(img_content)
        offset = offset+1