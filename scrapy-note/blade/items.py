# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QuoteItem(scrapy.Item):

    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()

class DouBanItem(scrapy.Item):

    title = scrapy.Field()
    author = scrapy.Field()
    createtime = scrapy.Field()
    comments = scrapy.Field()
