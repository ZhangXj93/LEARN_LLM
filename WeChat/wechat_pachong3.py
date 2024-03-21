import os,json,time
from selenium import webdriver
 
def crawel_url(url):
    
    # 创建Chrome WebDriver对象
    driver = webdriver.Chrome()
 
    print('-'*100)
    print(f'now: url: {url}')
    driver.get(url)
 
    # 添加适当的等待时间或条件，确保页面已完全加载
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # 等待10秒钟，直到某个元素可见
    wait = WebDriverWait(driver, 10)
    element = driver.find_element("xpath", "/html/body/div[1]/div[2]/div[1]/div/div[1]/div[2]")
    content = element.text
    print(content)

    driver.close()
 
url_list =[
    'https://mp.weixin.qq.com/s/2m8MrsCxf5boiH4Dzpphrg',
]

for url in url_list:
    crawel_url(url)
    time.sleep(5)