# -*- coding: utf-8 -*-
import scrapy
import os
import time
from blade.items import DouBanItem

class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["baidu.com"]
    url = "https://www.douban.com/group/futianzufang/"
    # url = "http://top.baidu.com/?fr=mhd_card"
    # url = "https://www.douban.com/gallery/topic/131026/?from=hot_topic_anony_sns"
    # url = 'http://quotes.toscrape.com/'

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url,
            callback=self.parse
        )

    def parse(self, response):
        print(" *************\n %s \n *************" % (response.request.headers))
        self._save_log(response.text)
        doubans = response.css('.douban')
        for douban in doubans:
            item = DouBanItem()
            # item['tags'] = douban.css('.tags .tag::text').extract()
            yield item

        next = response.css('.pager .next a::attr(href)').extract_first()
        url = response.urljoin(next)
        yield scrapy.Request(url=url, callback=self.parse)

    def _get_full_filename(self,filename,dir):
        dir_name = os.path.join(os.getcwd(),dir)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        full_name = os.path.join(dir_name,filename)
        # 确保被创建
        if not os.path.isfile(full_name):
            with open(full_name,'a+',encoding="utf-8") as f:
                f.close()
        return full_name

    def _save_log(self,msg):
        datastr = time.strftime("%Y-%m-%d", time.localtime())
        logfile_name = self._get_full_filename(datastr + ".log",'logs')
        if msg is not None:
            with open(logfile_name,'a+',encoding="utf-8") as f:
                f.write(msg + "\n")
