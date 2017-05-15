import requests
from bs4 import BeautifulSoup

def getRequest(url):
    kv={'user-agent':'Mozilla/5.0'}
    r = requests.get(url,headers=kv)
    return r

def parserHtml(r):
    soup = BeautifulSoup(r.content,"html.parser")
    houseSet = []
    houseList = soup(id="house-lst")
    for house in houseList[0].contents:
        if len(house) == 2:
            houseInfo = {}
            houseName = house.find('h2').string
            houseInfo['name'] = houseName
            
            houseUrl = house.find_all('a')
            houseUrl = houseUrl[0]
            href = houseUrl.attrs['href']
            houseInfo['href'] = href
            housePrice = house.find_all(class_="num")
            houseInfo['price'] = housePrice[0].string
            #print(houseInfo)
            houseSet.append(houseInfo)

    pageTag = soup(class_="page-box house-lst-page-box")
    pageTag = pageTag[0].attrs['page-data']
    page = eval(pageTag)
    curPage = page['curPage']
    if page['totalPage'] == page['curPage']:
        curPage = 0
    
    return houseSet,curPage

def crawData(curPage):
    houseSet = []
    print(curPage)
    baseUrl = 'http://sz.lianjia.com/zufang/pg'
    parmUrl = 'l1brp1000erp2500/'
    url = baseUrl+str(curPage)+parmUrl
    r = getRequest(url)
    houseList,curPage = parserHtml(r)
    houseSet.append(houseList)
    if curPage != 0:
        curPage += 1
        crawData(curPage)
    return houseSet

def main():
    houseSet = crawData('1')
    print(len(houseSet))

main()
            
            
