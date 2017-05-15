#coding=utf-8
import codecs
import requests
from bs4 import BeautifulSoup

class Crawler(object):
    def __init__(self,url,headers):
        self.url = url
        self.headers = headers

    def crawl(self,url,headers):
        print(url)
        return requests.get(url,headers=headers)

    def run(self):
        return self.parseBody(self.crawl(self.url,self.headers))


class JJGCrawler(Crawler):

    def parseBody(self,response):
        soup = BeautifulSoup(response.content,"html.parser")
        #print(soup)
        #body = soup.find_all(class_="article_content")
        body = soup.select(".article-content p")
        return body

def main():
    #模拟头文件
    headers = {'content-type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
    url = "http://blog.csdn.net/pleasecallmewhy/article/details/8925978"
    url = "http://cuiqingcai.com/1319.html"
    jjgCrawler = JJGCrawler(url,headers)
    html = jjgCrawler.run()
    print(type(html))
    
    for line in html:
        print(type(line))
        print(line)

    print("打印结束")
    html = str(html)

    #采用unicode方式读写
    outfile = codecs.open('d:\\newFile3.txt','w','utf-8')
    outfile.writelines(html)
    outfile.close()

main()
