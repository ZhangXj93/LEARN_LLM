import os,json,time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
 
def crawel_url(url):
    
    # 创建Chrome WebDriver对象
    driver = webdriver.Chrome()
 
    print('-'*100)
    print(f'now: url: {url}')
    driver.get(url)
 
    # 等待页面加载完成
    # 添加适当的等待时间或条件，确保页面已完全加载
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # 等待10秒钟，直到某个元素可见
    wait = WebDriverWait(driver, 10)
    # element = wait.until(EC.visibility_of_element_located((BY.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[1]/div[2]/section[5]")))
    element = driver.find_element("xpath", "/html/body/div[1]/div[2]/div[1]/div/div[1]/div[2]")
    content = element.text
    print(content)

    driver.close()
 
 
def download_urls(url_list, name_list, save_root):
    for url, name in zip(url_list, name_list):
        crawel_url(url)
        time.sleep(5)
 
 
 
url_list =[
    'https://mp.weixin.qq.com/s/MsQNXtzutoJHodlJEG4CJQ',
    'https://mp.weixin.qq.com/s/GST6zza7h0S0KH4bapRlxA',
    'https://mp.weixin.qq.com/s/5iHoKScTBwixN0Ob8o5tvw'
]
name_list = [
    'test.pdf', 'test1.pdf', 'test1.pdf'
]
save_root = 'D:\\GitHub\\LEARN_LLM\\WeChat\\'
download_urls(url_list, name_list, save_root)