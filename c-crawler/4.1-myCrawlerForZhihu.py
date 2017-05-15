#coding=utf-8
import time
import codecs
import requests
from bs4 import BeautifulSoup
from http import cookiejar

class AutoLogin():
    headers = {
        "Host":"www.zhihu.com",
        "Referer":"https://www.zhihu.com/",
        "User-Agent":"'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}"
    }

    session = requests.session()
    session.cookies = cookiejar.LWPCookieJar(filename='cookie.txt')
    try:
        print(session.cookies)
        session.cookies.load(ignore_discard = True)
    except:
        print("no cookie info")

    def getXsrf():
        response = session.get("https://www.zhihu.com",headers = headers)
        soup = BeautifulSoup(response.content,"html.parser")
        xsrf = soup.find("input",attrs={"name":"_xsrf"}).get("value")
        return xsrf

    #获取验证码
    def getCaptcha():
        t = str(int(time.time()*1000))
        captchaUrl = 'https://www.zhihu.com/captcha.gif?r='+t+"&type=login"
        r = session.get(captchaUrl,hearders=hearders)
        with open('captcha.jpg','wb') as f:
            f.write(r.content)
        captcha = input("验证码:")
        return captha
    def doLogin(email,password):
        loginUrl = "https://www.zhihu.com/login/email"
        data = {
            'email':email,
            'password':password,
            '_xsrf':getXsrf(),
            'captcha':getCaptcha(),
            'remember_me':'true'
        }
        response = session.post(loginUrl,data=data,headers=headers)
        loginCode = response.json()
        print(loginCode['msg'])
        for i in session.cookies:
            print(i)
        session.cookie.save()
        
    
#爬虫基类
class Crawler(object):
    def __init__(self,url,headers):
        self.url = url
        self.headers = headers

    def crawl(self,url,headers):
        print(url)
        return requests.get(url,headers=headers)

    def run(self):
        return self.parseBody(self.crawl(self.url,self.headers))


class ZhiHuCrawler(Crawler):
    def parseBody(self,response):
        soup = BeautifulSoup(response.content,"html.parser")
        #print(soup)
        #body = soup.find_all(class_="article_content")
        body = soup.select(".article-content p")
        return body

def main():
    #模拟头文件
    loginer = AutoLogin()
    email = "fictio@qq.com"
    password = "dk1108z0304"
    loginer.doLogin(email,password)
    url = "https://www.zhihu.com/"
    zhihuCrawler = ZhiHuCrawler(url,loginer.hearders)

    html = ZhiHuCrawler.run()
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
