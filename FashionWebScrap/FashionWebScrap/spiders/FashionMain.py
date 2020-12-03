from itertools import cycle
import requests
from lxml.html import fromstring
import scrapy
import re
import json
import pandas as pd
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings
from FashionWebScrap.FashionWebScrap.items import FashionWebScrapItem

data = pd.read_csv('C:\\Users\\Akki\\Desktop\\products.csv')


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies

class Myntra(scrapy.Spider):
    name = 'myntra'  # name variable is fixed
    start_urls = []
    for index, values in data.iterrows():

        if values['Seller'] == 'Myntra':
            start_urls.append(values['Product URL'])

    def parse(self, response):
        items = FashionWebScrapItem()

        script = ''.join(response.xpath('//script/text()')[1].extract())
        regex = re.compile(r'[\n\r\t]')
        script = regex.sub("", script)
        info = " ".join(script.split())
        data_obj = json.loads(info)

        items['seller'] = 'Myntra'
        items['pname'] = data_obj['name']
        items['uid'] = data_obj['mpn']
        items['bname'] = data_obj['brand']['name']
        items['stock'] = data_obj['offers']['availability']
        items['price'] = data_obj['offers']['price']
        items['img_url'] = data_obj['image']

        yield items


class Ajio(scrapy.Spider):
    name = 'ajio'  # name variable is fixed
    start_urls = []
    for index, values in data.iterrows():

        if values['Seller'] == 'Ajio':
            start_urls.append(values['Product URL'])

    def parse(self, response):
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
            items['stock'] = 'Out of Stock'

        urls = re.findall('(?:(?:https?|ftp):\/\/assets)+[\w/\-?=%.]+[MODEL\d*]+\.[.jpg]+', stockscript)

        items['pname'] = data_obj['name']
        items['seller'] = 'Ajio'
        items['uid'] = data_obj['mpn']
        items['bname'] = data_obj['brand']['name']
        items['price'] = data_obj['offers']['lowPrice']
        items['img_url'] = list(dict.fromkeys(urls))[0]

        yield items


class Amazon(scrapy.Spider):
    name = 'amazon'  # name variable is fixed
    start_urls = []
    for index, values in data.iterrows():
        if values['Seller'] == 'Amazon':
            start_urls.append(values['Product URL'])

    def parse(self, response):
        items = FashionWebScrapItem()

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
        img_url = response.css('div#imgTagWrapperId img::attr(src)').extract()
        items['img_url'] = img_url[0]

        if price:
            items['stock'] = "InStock"
        else:
            items['stock'] = "Out of Stock"
        items['price'] = price

        yield items

configure_logging()
runner = CrawlerRunner(get_project_settings())
@defer.inlineCallbacks
def crawl():
    yield runner.crawl(Myntra)
    yield runner.crawl(Ajio)
    yield runner.crawl(Amazon)
    reactor.stop()
crawl()
reactor.run()