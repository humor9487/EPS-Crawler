import asyncio
import time
from concurrent.futures.thread import ThreadPoolExecutor

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException


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

executor = ThreadPoolExecutor(3)
N = 5

count = 0
def scrape(stock, *, loop):
    loop.run_in_executor(executor, scraper, stock)


def scraper(stock):
    print(f"Ready to get: {stock}")
    try:
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get(f"https://invest.cnyes.com/usstock/detail/{stock}/earnings/estimate#fixed")
        # resultLocator = '//body'
        # WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.XPATH, resultLocator)))
        time.sleep(3)
        browser.execute_script("window.scrollTo(0, 2500)")
        # 待處理cookie按鈕
        for i in range(1, N):
            button = browser.find_elements("xpath",
                                           '//*[@id="anue-ga-wrapper"]/div[2]/div[3]/section/div/div/div/div[2]/div[4]/div[2]/button[1]')[
                0]
            if len(button.get_attribute("style")) > 0:
                break
            button.click()
            time.sleep(1)
    except (IndexError, ElementNotInteractableException):
        print(f"{stock} may only one page")
        with open(f"EPS_files/{stock}_EPS.txt", "w") as f:
            page_results = browser.find_elements("xpath", "//tbody")
            f.writelines(item.text for item in page_results)
        return
    except Exception as e:
        print(e)
        print(f"not found stock ticker {stock}")
        return
    try:
        with open(f"EPS_files/{stock}_EPS.txt", "w") as f:
            # print(browser.find_elements(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/section/div/div/div/div[2]/div[4]/div[3]/div[2]/span/a[1]"))
            for i in range(1, N + 1):
                WebDriverWait(browser, 2).until(
                    EC.visibility_of_element_located((By.XPATH, f'//*[@id="DataTables_Table_0_paginate"]/span/a[{i}]')))
                time.sleep(0.5)

                # buttonx = browser.find_elements(By.LINK_TEXT, str(i))
                # buttonx[0].click()

                actions = ActionChains(browser)
                actions.send_keys(Keys.TAB)
                actions.send_keys(Keys.ENTER)
                actions.perform()
                page_results = browser.find_elements("xpath", "//tbody")
                f.writelines(item.text for item in page_results)
        print(f"finish to get: {stock}")
    except TimeoutException:
        print(f"{stock} may not complete")
    except IndexError:
        print(f"{stock} IndexError on step 2")
    except:
        print(f"fail to get: {stock} error on step 2")

loop = asyncio.get_event_loop()

with open("stock_list.txt", "r") as f:
    stock_list = f.read().split()


for stock in stock_list[:20]:
    scrape(stock, loop=loop)

loop.run_until_complete(asyncio.gather(*asyncio.all_tasks(loop)))