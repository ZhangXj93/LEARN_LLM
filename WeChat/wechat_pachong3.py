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
 
    # # 获取当前所有窗口的句柄
    # handles = driver.window_handles
    # # 切换到最后一个窗口（假设最后一个窗口是要操作的窗口）
    # driver.switch_to.window(handles[-1])
 
 
    # # 获取当前视口的高度
    # viewport_height = driver.execute_script("return window.innerHeight;")
    # # 获取滚动条的位置
    # current_scroll_position = driver.execute_script("return window.scrollY;")
 
    # # 定义滚动的距离和间隔时间
    # # scroll_distance = 200 # 每次滚动的距离
    # # scroll_interval = 0.5 # 每次滚动的间隔时间（秒）
 
    # # 计算需要滚动的次数
    # num_scrolls = int((driver.execute_script("return document.body.scrollHeight;") - current_scroll_position) / scroll_distance)
 
    # print('scroll pages...')
    # # 循环滚动页面
    # for _ in range(num_scrolls):
    #     driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    #     time.sleep(scroll_interval)
 
    # # 执行 JavaScript 代码，将页面滚动到底部
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
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