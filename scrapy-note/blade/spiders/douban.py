# -*- coding: utf-8 -*-
import scrapy
import os
import time
from blade.items import DouBanItem

class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["www.douban.com"]
    url = "https://www.douban.com/group/futianzufang/discussion?start="
    page = 0

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url + str(self.page),
            callback=self.parse
        )

    def parse(self, response):
        self.logger.info('Douban page: %s', response.url)
        hrefs = response.css('.olt .title a::attr(href)').extract()
        for href in hrefs:
            if href:
                yield scrapy.Request(url=href, callback=self.parse_detail)
            time.sleep(4)
        self.page += 25
        print("URL: %s%s" % (self.url,self.page))
        if self.page <= 50:
            yield scrapy.Request(url=self.url + str(self.page), callback=self.parse)

    def parse_detail(self, response):
        item = DouBanItem()
        topic_content = response.css('#topic-content')
        item['article_url'] = response.url
        item['article_title'] = self._content_format(topic_content.css('.infobox td::text').extract())
        item['article_content'] = self._content_format(topic_content.css('.topic-richtext p::text').extract())
        item['article_imgs'] = topic_content.css('.topic-richtext img::attr(src)').extract()
        item['create_time'] = topic_content.css('h3 .color-green::text').get()
        author = topic_content.css('.user-face')
        item['author_url'] = author.css('a::attr(href)').get()
        item['author_name'] = author.css('img::attr(alt)').get()
        item['author_img'] = author.css('img::attr(src)').get()
        comment_slector = response.css('#comments li')
        comment_list = []
        for comment_row in comment_slector:
            comment_list.append(self._build_comment(comment_row))
        item['comments'] = comment_list
        yield item

    def _build_comment(self, comment_row):
        name = comment_row.css('img::attr(alt)').get()
        img = comment_row.css('img::attr(src)').get()
        url = comment_row.css('.user-face a::attr(href)').get()
        content = comment_row.css('.reply-content::text').extract()
        return name + "|" + img + "|" + url + "|" + self._content_format(content)

    # 将list中的内容进行拼接，形成字符串
    def _content_format(self,in_list):
        result = ''
        for list_item in in_list:
            result = result + list_item

        return result

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
