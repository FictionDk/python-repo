# -*- coding: utf-8 -*-
import scrapy
import os
import time
from blade.items import DouBanItem

class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["baidu.com"]
    url = "https://www.douban.com/group/futianzufang/discussion?start="
    # url = "http://top.baidu.com/?fr=mhd_card"
    # url = "https://www.douban.com/gallery/topic/131026/?from=hot_topic_anony_sns"
    # url = 'http://quotes.toscrape.com/'
    page = 0

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url + str(self.page),
            callback=self.parse
        )

    def parse(self, response):
        self.logger.info('Douban page: %s', response.url)
        result_tables = response.xpath('//table')
        tr_rows = None
        if(result_tables is not None and len(result_tables) > 1):
            tr_rows = result_tables[1].xpath('tr')
        for tr_row in tr_rows:
            item = self._build_douban_item(tr_row)
            yield item
        time.sleep(4)
        self.page += 25
        print("URL: %s%s" % (self.url,self.page))
        if self.page <= 100:
            yield scrapy.Request(url=self.url + str(self.page), callback=self.parse)

    def _build_douban_item(self,tr_row):
        td_rows = tr_row.xpath('td')
        item = DouBanItem()
        item['article_url'] = td_rows[0].xpath('a/@href').get()
        item['article_title'] = td_rows[0].xpath('a/@title').get()
        item['author_url'] = td_rows[1].xpath('a/@href').get()
        item['author_name'] = td_rows[1].xpath('a/text()').get()
        item['createtime'] = td_rows[3].xpath('text()').get()
        return item

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
