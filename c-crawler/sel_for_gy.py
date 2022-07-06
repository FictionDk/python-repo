from selenium import  webdriver
from selenium.webdriver.common.by import By
import time,os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = "logs"

# 最新驱动地址: https://sites.google.com/chromium.org/driver/
def _get_driver_path():
    return os.path.join('E:',os.path.sep,'NutDoc','res','chromedriver.exe')

def _build_browser(driver_path):
    browser = webdriver.Chrome(driver_path)
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('--headless')  # 无头
    #chrome_options.add_argument('--disable-gpu')  # 无GPU
    browser = webdriver.Chrome(driver_path, options=chrome_options)  # 构建一个chrome对象
    return browser

def _get_snapshot_path(sp_name):
    return os.path.join(BASE_DIR,LOGS_DIR,sp_name)

browser = _build_browser(_get_driver_path())  # 构建


browser.get('https://libproxy.ruc.edu.cn/ermsClient/eresourceInfo.do?rid=62') # 进入图书馆国研网界面
time.sleep(3)

login_user_page = browser.find_element(By.XPATH, '/html/body/div[3]/div[1]/div[1]/div[1]/div/div[2]/ul/li[1]/a')
login_user_page.click()#点击国研网按钮
time.sleep(10)#迅速输入vpn账号密码


windows = browser.window_handles# 获取所有窗口
browser.switch_to.window(windows[-1])# 切换到当前最新打开的窗口

browser.switch_to.frame("login-iframe")

username_input = browser.find_element_by_name('username')
username_input.click()
username_input.send_keys('2020102555')

passport_input = browser.find_element(By.NAME,'passport')#通过标签的id属性值定位密码输入框
mima_user_page = browser.find_element(By.XPATH, '/html/body/div/form/div[4]/input')
mima_user_page.click()#点击密码框

passport_input.send_keys('anjdRUCer12345')#输入密码

print("start login by user")
time.sleep(25)
print("end login by user")

#第二步：进入国研网后到达对外贸易数据库
windows = browser.window_handles# 获取所有窗口
browser.switch_to.window(windows[-1])# 切换到当前最新打开的窗口
choice_user_page = browser.find_element(By.XPATH,'/html/body/div[3]/div/ul/li[4]/a')
choice_user_page.click()
time.sleep(3)
windows = browser.window_handles# 获取所有窗口
browser.switch_to.window(windows[-1])# 切换到当前最新打开的窗口
hongguanjingji_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[1]/div[2]/div[2]/ul/li[3]/span')
hongguanjingji_user_page.click()
#定位并选择宏观经济数据库
duiwaimaoyi_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[1]/div[2]/div[2]/ul/li[3]/ul/li[9]/a')
duiwaimaoyi_user_page.click()
#定位并选择对外贸易

#第三步：开始设置筛选条件
windows = browser.window_handles# 获取所有窗口
browser.switch_to.window(windows[-1])# 切换到当前最新打开的窗口
time.sleep(2)

#选择年份
gaojichaxun_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[1]/div[1]/div/div/ul/li[2]/span')
gaojichaxun_user_page.click()#点开高级查询
year_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[1]/div[1]/div/div/ul/li[2]/ul/li[17]')
year_user_page.click()#选择2006年数据
time.sleep(1)
#选择地区
diqu_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[1]/ul/li[1]')
diqu_user_page.click()#选择地区
time.sleep(3)
quanguo_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/span[1]')
quanguo_user_page.click()#点开全国
time.sleep(1)
beijing_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[1]/div[1]/label/span/span')
beijing_user_page.click()#选择北京数据
tianjin_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[1]/label/span/span')
tianjin_user_page.click()#选择天津数据
hebei_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[3]/div[1]/label/span/span')
hebei_user_page.click()#选择河北数据
time.sleep(1)
#选择海关代码
haiguan_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[1]/ul/li[2]')
haiguan_user_page.click()#选择海关
time.sleep(1)
haiguandaima_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/span[1]')
haiguandaima_user_page.click()#点开海关代码
time.sleep(1)
di1lei_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[1]/div[1]/label/span/span')
di1lei_user_page.click()#选择第一类
di2lei_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[2]/div[1]/label/span/span')
di2lei_user_page.click()#选择第二类
di3lei_user_page = browser.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/div/div/div[1]/div[11]/div[2]/div[2]/div/div[1]/div[2]/div/div[1]/div[2]/div[3]/div[1]/label/span/span')
di3lei_user_page.click()#选择第三类
time.sleep(5)
#browser.close()