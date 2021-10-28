# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.http import HtmlResponse
from time import sleep
import random
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class BladeSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# 首先在scrapy的middware中定义一个middware类
class RandomUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self,user_agent=''):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('USER_AGENT_LIST')
        )

    # 重定义process_requests方法：
    def process_requests(self, request, spider):
        rand_use = random.choice(self.user_agent)
        if rand_use:
            request.headers.setdefault('User-Agent', rand_use)

class IoliuResponseMiddleware(object):

    def _get_snapshot_path(self,file_path):
        return os.path.join(BASE_DIR,file_path)

    def process_response(self, request, response, spider):
        if "ioliu" == spider.name:
            spider.browser.get(url=request.url)
            sleep(random.randint(3,5))
            screenshot_path = self._get_snapshot_path('a.png')
            spider.browser.get_screenshot_as_file(screenshot_path)
            sleep(3)
            row_response = spider.browser.page_source
            return HtmlResponse(url=spider.browser.current_url,body=row_response,encoding="utf8",request=request)
        else:
            return response
