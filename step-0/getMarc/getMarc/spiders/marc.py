#%% Libraries
import re
import urllib
import scrapy
import pandas as pd
from scrapy.loader import ItemLoader
from getMarc.items import rawEmail, rawRelations
from lxml import html
#%% define
class marcMails(scrapy.Spider):
    name = 'marc'
    base_url = 'https://marc.info/'
    mailing_list = 'python-dev'

    def start_requests(self):
        #--+ get urls level 0
        urls = []
        for y in range(1999,2000,1):
            for m in range(1,13,1):
                if m<10:
                    urls.append("https://marc.info/?l={}&r=1&b={}0{}&w=2".format(self.mailing_list,y,m))
                else:
                    urls.append("https://marc.info/?l={}&r=1&b={}{}&w=2".format(self.mailing_list,y,m))
        #--+ start parsing
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse,)
    
    def parse(self, response):
        #--+ get urls
        _xpt = "//pre//@href"
        _get_urls = response.xpath(_xpt).extract()
        #--+ get email
        email_urls = [self.base_url + i for i in _get_urls if '&m=' in i]
        # relations
        for url in email_urls:
            yield scrapy.Request(url, callback=self.parse_relations)
        email_urls = [i.replace('&w=2', '&q=mbox') for i in email_urls]
        # body
        for url in email_urls:
            yield scrapy.Request(url, callback=self.parse_email)
        #--+ get thread
        thread_urls = [self.base_url + i for i in _get_urls if '?t=' in i]
        for url in thread_urls:
            yield scrapy.Request(url, callback=self.parse_thread)
        #--+ new page
        _xpt = "//pre//a[contains(text(), 'Next')][1]//@href"
        next_url = response.xpath(_xpt).extract()
        if any(next_url):
            next_url = self.base_url + next_url[0]
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_thread(self, response):
        #--+ get urls
        _xpt = "//pre//@href"
        _get_urls = response.xpath(_xpt).extract()
        #--+ get email
        email_urls = [self.base_url + i for i in _get_urls if '&m=' in i]
        # relations
        for url in email_urls:
            yield scrapy.Request(url, callback=self.parse_relations)
        email_urls = [i.replace('&w=2', '&q=mbox') for i in email_urls]
        # body
        for url in email_urls:
            yield scrapy.Request(url, callback=self.parse_email)
        #--+ new page
        _xpt = "//pre//a[contains(text(), 'Next')][1]//@href"
        next_url = response.xpath(_xpt).extract()
        if any(next_url):
            next_url = self.base_url + next_url[0]
            yield scrapy.Request(next_url, callback=self.parse_thread)
    
    def parse_email(self, response):
        load = ItemLoader(item = rawEmail(), selector=response)
        #--+ pass url
        _url = response.url
        load.add_value('url', _url)
        #--+ pass email_id
        _id = re.findall('&m=(.*)&q=', _url)[0]
        load.add_value('_id', _id) 
        #--+ get raw email
        _raw = response.text
        load.add_value('rawBody', _raw) 
        return load.load_item()
    
    def parse_relations(self, response):
        load = ItemLoader(item = rawRelations(), selector=response)
        #--+ focal url
        focal_url = response.url
        load.add_value('focal_url', focal_url)
        #--+ following url
        next_url = response.xpath("//pre//a[contains(text(), 'next in thread')][1]//@href").extract()
        if len(next_url)==2:
            next_url = self.base_url + next_url[0]
        elif len(next_url)==0:
            next_url = ''
        load.add_value('next_url', next_url)
        #--+ previous url
        prev_url = response.xpath("//pre//a[contains(text(), 'prev in thread')][1]//@href").extract()
        if len(prev_url)==2:
            prev_url = self.base_url + prev_url[0]
        elif len(prev_url)==0:
            prev_url = ''
        load.add_value('prev_url', prev_url)
        return load.load_item()