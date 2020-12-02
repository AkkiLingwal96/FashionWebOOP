# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FashionWebScrapItem(scrapy.Item):
    # define the fields for your item here like:
    uid = scrapy.Field()
    bname = scrapy.Field()
    stock = scrapy.Field()
    price = scrapy.Field()
    img_url = scrapy.Field()
    seller = scrapy.Field()
    pname = scrapy.Field()
