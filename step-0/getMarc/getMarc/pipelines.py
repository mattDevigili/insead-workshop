# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter


class ScrapingmarcPipeline:
    def process_item(self, item, spider):
        return item

class JsonWriterPipeline:

    def open_spider(self, spider):
        self.file_0 = open('{}_rawBody.jsonl'.format(spider.name), 'w')
        self.file_1 = open('{}_relations.jsonl'.format(spider.name), 'w')

    def close_spider(self, spider):
        self.file_0.close()
        self.file_1.close()

    def process_item(self, item, spider):
        d = ItemAdapter(item).asdict()
        if '_id' in d:
            line = json.dumps(d) + "\n"
            self.file_0.write(line)
        elif 'focal_url' in d:
            line = json.dumps(d) + "\n"
            self.file_1.write(line) 
        return item