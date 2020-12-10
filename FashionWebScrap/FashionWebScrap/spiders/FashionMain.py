# For Regex, JSON and URL Extract
import tldextract
import re
import json

# For Product csv read
import pandas as pd

# For Scrapy
import scrapy
from scrapy import FormRequest
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings
from FashionWebScrap.FashionWebScrap.items import FashionWebScrapItem

# For Proxies
import requests
from lxml.html import fromstring


# def get_proxies():
#     url = 'https://free-proxy-list.net/'
#     response = requests.get(url)
#     parser = fromstring(response.text)
#     proxies = set()
#     for i in parser.xpath('//tbody/tr'):
#         if i.xpath('.//td[7][contains(text(),"yes")]'):
#             # Grabbing IP and corresponding PORT
#             proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
#             proxies.add(proxy)
#     return proxies

# Scraping Myntra
class Myntra(scrapy.Spider):

    def parse_myntra(self, response):
        items = FashionWebScrapItem()

        script = ''.join(response.xpath('//script/text()')[1].extract())
        regex = re.compile(r'[\n\r\t]')
        script = regex.sub("", script)
        info = " ".join(script.split())
        data_obj = json.loads(info)

        imgs = ''.join(response.xpath('//script/text()')[9].extract())
        imgs = regex.sub("", imgs)
        info2 = " ".join(imgs.split())
        info2 = info2.replace("window.__myx = ", "")
        imgs_obj = json.loads(info2)

        items['seller'] = 'Myntra'
        items['pname'] = data_obj['name']
        items['uid'] = data_obj['mpn']
        items['bname'] = data_obj['brand']['name']
        items['stock'] = data_obj['offers']['availability']
        items['price'] = data_obj['offers']['price']
        items['img_urls'] = []

        for value in imgs_obj['pdpData']['media']['albums'][0]['images']:
            items['img_urls'].append(value['imageURL'])

        yield items


# Scraping Reliance Ajio
class Ajio(scrapy.Spider):

    def parse_ajio(self, response):
        items = FashionWebScrapItem()
        script = ''.join(response.xpath('//script/text()')[4].extract())
        stockscript = ''.join(response.xpath('//script/text()')[9].extract())
        regex = re.compile(r'[\n\r\t]')
        script = regex.sub("", script)
        info = " ".join(script.split())
        data_obj = json.loads(info)

        stock = re.findall(r'inStock', stockscript)
        if stock:
            items['stock'] = 'InStock'
        else:
            items['stock'] = 'OutOfStock'

        urls = re.findall('(?:(?:https?|ftp):\/\/assets)+[\w/\-?=%.]+[MODEL\d*]+\.[jpg]+', stockscript)

        items['img_urls'] = []
        u_img = list(dict.fromkeys(urls))

        for value in u_img:
            if value.find("-473Wx593H") != -1:
                items['img_urls'].append(value)

        items['pname'] = data_obj['name']
        items['seller'] = 'Ajio'
        items['uid'] = data_obj['mpn']
        items['bname'] = data_obj['brand']['name']
        items['price'] = data_obj['offers']['lowPrice']

        yield items


# Scraping Koovs.com
class Koovs(scrapy.Spider):

    def parse_koovs(self, response):
        items = FashionWebScrapItem()

        script = ''.join(response.xpath('//script/text()')[1].extract())
        regex = re.compile(r'[\n\r\t]')
        script = regex.sub("", script)
        info = " ".join(script.split())
        data_obj = json.loads(info)

        stock = ''.join(response.xpath('//script/text()')[7].extract())
        stock = regex.sub("", stock)
        info2 = " ".join(stock.split())
        info2 = info2.replace("window.__INITIAL_STATE__ = ", "")
        stock_obj = json.loads(info2)

        availability = stock_obj["productPage"]["productData"]["isProductOutOfStock"]
        img_urls = stock_obj["productPage"]["productData"]["imageUrls"]

        items['seller'] = 'Koovs'
        items['pname'] = data_obj['name']
        items['uid'] = data_obj['mpn']
        items['bname'] = data_obj['brand']['name']
        items['price'] = data_obj['offers']['price']
        items['img_urls'] = img_urls

        if availability == False:
            items['stock'] = "inStock"
        else:
            items['stock'] = "OutOfStock"

        yield items


# Scraping Amazon
class Amazon(scrapy.Spider):

    def parse_amazon(self, response):
        items = FashionWebScrapItem()

        regex = re.compile(r'[\n\r\t]')
        script = ''.join(response.xpath('//*[contains(text(), "colorImages")]')[0].extract())
        script = regex.sub("", script)

        urls = re.findall('(?:(?:https?|ftp):\/\/)+[\w/\-?=%.]+\.[jpg]+', script)

        items['img_urls'] = []
        u_img = list(dict.fromkeys(urls))

        flag = 0
        for value in u_img:
            if value.find("UL1440") != -1 or value.find("UL1500") != -1:
                items['img_urls'].append(value)
                flag = 1
            elif value.find("UX466") != -1 and flag == 0:
                items['img_urls'].append(value)

        title = response.xpath('//h1[@id="title"]/span/text()').extract()
        sale_price = response.xpath('//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()').extract()
        regex = re.compile(r'₹\xa0')
        sale_price = ''.join(sale_price).strip()
        price = regex.sub("", sale_price)

        items['pname'] = ''.join(title).strip()
        items['seller'] = 'Amazon'

        pid = self.start_urls[0].rsplit('/', 1)[1]
        items['uid'] = pid
        items['bname'] = items['pname'].split()[0]

        if price:
            items['stock'] = "InStock"
        else:
            items['stock'] = "OutOfStock"
        items['price'] = price

        yield items


# Scraping Forever21
class Forev(scrapy.Spider):

    def parse_forev(self, response):
        items = FashionWebScrapItem()

        script = ''.join(response.xpath('//script/text()')[9].extract())
        regex = re.compile(r'[\n\r\t]')
        script = regex.sub("", script)
        info = " ".join(script.split())
        data_obj = json.loads(info)

        items['img_urls'] = []

        items['seller'] = 'Forever21'
        items['pname'] = data_obj['name']
        items['uid'] = data_obj['sku']
        items['bname'] = data_obj['brand']['name']
        items['price'] = data_obj['offers'][0]['price']

        stock = data_obj['offers'][0]['availability']
        stock = stock.split('/')

        items['stock'] = stock[3]

        items['img_urls'].append(data_obj['image'])

        yield items


# Function to fetch DNS of the URL
def getdns(url):
    ext = tldextract.extract(url)
    return ext.domain


# Main Class Body
class Main(Myntra, Ajio, Forev, Koovs, Amazon):

    name = "fashion_web_scraper"

    data = pd.read_csv('C:\\Users\\Akki\\Desktop\\products.csv')
    start_urls = []
    for index, values in data.iterrows():
        if values['Seller'] == 'Myntra':
            start_urls.append(values['Product URL'])
        elif values['Seller'] == 'Ajio':
            start_urls.append(values['Product URL'])
        elif values['Seller'] == 'Amazon':
            start_urls.append(values['Product URL'])
        elif values['Seller'] == 'Koovs':
            start_urls.append(values['Product URL'])
        elif values['Seller'] == 'Forev':
            start_urls.append(values['Product URL'])
        else:
            continue

    # proxies = get_proxies()
    # with open("proxies.txt", 'w') as file:
    #     for row in proxies:
    #         s = "".join(map(str, row))
    #         file.write(s + '\n')

    def parse(self, response):
        url = response.url
        dns = getdns(url).lower()
        if dns == "myntra":
            yield FormRequest(url=response.url, callback=self.parse_myntra)
        elif dns == "ajio":
            yield FormRequest(url=response.url, callback=self.parse_ajio)
        elif dns == "amazon":
            yield FormRequest(url=response.url, callback=self.parse_amazon)
        elif dns == "koovs":
            yield FormRequest(url=response.url, callback=self.parse_koovs)
        elif dns == "forever21":
            yield FormRequest(url=response.url, callback=self.parse_forev)


# -- do not touch this area --
configure_logging()
runner = CrawlerRunner(get_project_settings())


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(Main)
    reactor.stop()


crawl()
reactor.run()

# process = CrawlerProcess(get_project_settings())
# process.crawl(Main)
# process.start()
