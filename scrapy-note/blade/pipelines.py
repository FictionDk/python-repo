from scrapy.exceptions import DropItem


class TextPipeline(object):
    def __init__(self):
        self.limit = 50

    def process_item(self, item, spider):
        if item['text']:
            if len(item['text']) > self.limit:
                item['text'] = item['text'][0:self.limit].rstrip() + '...'
            return item
        else:
            return DropItem('Missing Text')

class AuthorPipeline(object):

    def process_item(self, item, spider):
        print(">>>>author: ",item['author'])
        return item
