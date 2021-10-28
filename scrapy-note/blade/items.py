# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class BaseItem(scrapy.Item):
    article_id = scrapy.Field()
    article_title = scrapy.Field()
    article_content = scrapy.Field()
    article_url = scrapy.Field()
    article_imgs = scrapy.Field()
    author_url = scrapy.Field()
    author_name = scrapy.Field()
    author_img = scrapy.Field()
    author_id = scrapy.Field()
    create_time = scrapy.Field()
    comments = scrapy.Field()

class QuoteItem(scrapy.Item):
    item_from = "quote"
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()

class DouBanItem(BaseItem):
    item_from = "douban"

class IoliuItem(BaseItem):
    item_from = "ioliu"
    img_url = scrapy.Field()
    img_name = scrapy.Field()

