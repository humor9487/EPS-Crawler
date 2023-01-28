#爬蟲程式定義
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException
from concurrent.futures.thread import ThreadPoolExecutor

finished = set(map(lambda x: x[:-8], os.listdir("EPS_files")))
# get N * 50 season data
N = 5
load_time = 0.3
# how many thread to create
Thread_number = 4

chrome_options = webdriver.ChromeOptions()
# 添加 User-Agent
chrome_options.add_argument(
    'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"')
# 指定瀏覽器解析度
chrome_options.add_argument('window-size=1920x1080')
# 不載入圖片，提升速度
chrome_options.add_argument('blink-settings=imagesEnabled=false')
# 瀏覽器不提供視覺化頁面
chrome_options.add_argument('--headless')
# 最高權限
chrome_options.add_argument('--no-sandbox')
# 改寫docker記憶體位置
chrome_options.add_argument('--disable-dev-shm-usage')

drivers = [webdriver.Chrome("/usr/bin/chromedriver", chrome_options=chrome_options) for _ in range(Thread_number)]

def keybroad_action(browser, key, repeat=1, sleep=0):

    for _ in range(repeat):
        actions = ActionChains(browser)
        actions.send_keys(key)
        actions.perform()
        time.sleep(sleep)
    return

def crawing(stock, browser):
    if stock in finished:
      print(f"{stock} already collected")
      return
    print(f"Ready to get: {stock}")
    try:
        browser.get(f"https://invest.cnyes.com/usstock/detail/{stock}/earnings/estimate#fixed")
        
        time.sleep(3)
        keybroad_action(browser, Keys.TAB, 19)
        keybroad_action(browser, Keys.ENTER, N - 1, load_time)
    except Exception as e:
        print(e)
        print(f"not found stock ticker {stock}")
        return
    try:
        with open(f"EPS_files/{stock}_EPS.txt", "w") as f:
            page_results = browser.find_elements("xpath", "//tbody")
            f.writelines(item.text for item in page_results)
            keybroad_action(browser, Keys.TAB)
            for i in range(1, N):
                WebDriverWait(browser, 1).until(
                    EC.visibility_of_element_located((By.XPATH, f'//*[@id="DataTables_Table_0_paginate"]/span/a[{i}]')))
                time.sleep(load_time)
                keybroad_action(browser, Keys.TAB)
                keybroad_action(browser, Keys.ENTER)
                page_results = browser.find_elements("xpath", "//tbody")
                f.writelines(item.text for item in page_results)
        print(f"finish to get: {stock}")
    except TimeoutException:
        print(f"got {i} page on {stock}")
    except IndexError:
        print(f"{stock} IndexError on step 2")
    except:
        print(f"other exception on {stock} on step 2")
#爬蟲程式執行
with open("stock_list.txt", "r") as f:
    stock_list = f.read().split()

for i in range(0, len(stock_list), Thread_number):
  with ThreadPoolExecutor(max_workers=Thread_number) as executor:
    bucket = executor.map(crawing, stock_list[i:i+Thread_number], drivers)
