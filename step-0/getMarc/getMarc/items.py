# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class rawEmail(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    rawBody = scrapy.Field()
    pass

class rawRelations(scrapy.Item):
    focal_url = scrapy.Field()
    next_url = scrapy.Field()
    prev_url = scrapy.Field()
    pass