# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo

class FashionWebScrapPipeline:

    def __init__(self):
        self.conn = pymongo.MongoClient(
            'localhost', 27017
        )
        db = self.conn['fashiondb']
        self.collection = db['fashion_tb']

    def process_item(self, item, spider):
        myquery = {'uid': item['uid']}
        self.collection.delete_one(myquery)
        self.collection.insert(dict(item))
        print(item)
        return item
