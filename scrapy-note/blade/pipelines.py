from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
import os
import time
import json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class BuildItemIDPipeline(object):

    def process_item(self, item, spider):
        if "douban" == spider.name and "article_url" in item and item['article_url']:
            article_url = item['article_url']
            splits = article_url.split('/')
            item['article_id'] = splits[len(splits) - 2]
            splits = item['author_url'].split('/')
            item['author_id'] = splits[len(splits) - 2]
            return item
        elif "ioliu" == spider.name:
            return item
        else:
            return DropItem("Missing ...")

class JsonWriterPipeline(object):
    def __init__(self):
        datastr = time.strftime("%Y-%m-%d", time.localtime())
        self.full_name = self.__get_full_filename(datastr + '.jl','logs')

    def process_item(self, item, spider):
        # spider.logger.info("ITEM: %s" % json.dumps(dict(item),ensure_ascii=False))
        self.__save_log(json.dumps(dict(item),ensure_ascii=False))
        return item

    def __get_full_filename(self,filename,dir):
        dir_name = os.path.join(BASE_DIR,dir)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        full_name = os.path.join(dir_name,filename)
        # 确保被创建
        if not os.path.isfile(full_name):
            with open(full_name,'a+',encoding="utf-8") as f:
                f.close()
        return full_name

    def __save_log(self,msg):
        if msg is not None:
            with open(self.full_name,'a+',encoding="utf-8") as f:
                f.write(msg + "\n")

class ImagespiderPipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        print("BASE_DIR= %s" % self.store)
        print("INFO = ",info)
        print("item:( %s : %s )" % (item['img_url'],item['img_name']))
        yield Request(item['img_url'])

    # 重写命名函数，否则图片名为哈希值
    # def file_path(self, request, response=None, info=None):
    #    media_guid = request.meta['name']
    #    media_ext = os.path.splitext(request.url)[1]
    #    self.logger.info("........... ",media_guid)
    #    print("**********name:( %s )" % media_guid)
    #    return 'full/%s%s' % (media_guid, media_ext)
