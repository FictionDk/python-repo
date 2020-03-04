# -*- coding: utf-8 -*-
import scrapy

from blade.items import DouBanItem


class QuotesSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["douban.com"]
    start_urls = ['https://douban.com/group/futianzufang/']

    def parse(self, response):
        doubans = response.css('.douban')
        for douban in doubans:
            item = DouBanItem()
            print(">>>>",douban)
            # item['tags'] = douban.css('.tags .tag::text').extract()
            yield item

        next = response.css('.pager .next a::attr(href)').extract_first()
        url = response.urljoin(next)
        yield scrapy.Request(url=url, callback=self.parse)
