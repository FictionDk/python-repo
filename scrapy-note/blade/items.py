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

    article_id = scrapy.Field()
    article_title = scrapy.Field()
    article_content = scrapy.Field()
    article_url = scrapy.Field()
    author_url = scrapy.Field()
    author_name = scrapy.Field()
    author_id = scrapy.Field()
    createtime = scrapy.Field()
    comments = scrapy.Field()
