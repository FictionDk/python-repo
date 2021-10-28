import scrapy
import os
from selenium import webdriver
from blade.items import IoliuItem

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = "logs"


class BingImgItemSpider(scrapy.Spider):
    name = "ioliu"
    allowed_domains = ["bing.ioliu.cn"]
    url = "https://bing.ioliu.cn"
    page = 1

    def __init__(self):
        driver_path = self._get_driver_path()
        self.browser = self._build_browser(driver_path)

    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url + '?p=' + str(self.page),
            callback=self.parse
        )

    def parse(self, response):
        self.logger.info('>>>> bing ioliu: %s', response.url)
        hrefs = response.css('.container .item .options .ctrl.download::attr(href)').extract()
        names = response.css('.container .item .description h3::text').extract()
        for index,href in enumerate(hrefs):
            print(">>> %d , %s , %s" % (index,href,names[index]))
            item = IoliuItem()
            item['img_url'] = self.url + href
            item['img_name'] = names[index]
            yield item
        self.page += 1
        if self.page <= 1:
            yield scrapy.Request(url=self.url + '?p=' + str(self.page), callback=self.parse)

    def _get_driver_path(self,own_machine=True):
        '''
        获取无头chrome驱动,cnpm镜像下载地址:
            http://npm.taobao.org/mirrors/chromedriver/
        '''
        if own_machine:
            return os.path.join('D:',os.path.sep,'Resource','chromedriver_win32','chromedriver.exe')
        else:
            return os.path.join('E:',os.path.sep,'OneDrive')

    def _build_browser(self,driver_path):
        '''
        构建无头浏览器对象,使用时注意对象的关闭和加载时间控制
        '''
        browser = webdriver.Chrome(driver_path)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')  # 无头
        chrome_options.add_argument('--disable-gpu')  # 无GPU
        browser = webdriver.Chrome(driver_path, options=chrome_options)  # 构建一个chrome对象
        return browser

    def close(self, spider):
        self.browser.close()
        self.browser.quit()
