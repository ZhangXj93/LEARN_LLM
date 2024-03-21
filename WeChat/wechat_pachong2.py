import os,json,time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
 
 
def print_url_to_pdf(url, save_root, 
                     file_name='demo.pdf', 
                     scroll_distance=500, 
                     scroll_interval=0.5, 
                     headless=False):
    """
    save_root: pdf 保存目录，建议绝对路径
    file_name：pdf保存名称
    scroll_distance：每次向下滑动距离，模拟浏览页面，获得全部页面元素
    scroll_interval：滑动一次后，间隔时间
    headless：是否可见窗口，True, 不可见；False，可见，调试时可设为可见
    """
    chrome_options = webdriver.ChromeOptions()
 
    settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,
        "isHeaderFooterEnabled": False,
 
        # "customMargins": {},
        # "marginsType": 2,
        # "scaling": 100,
        # "scalingType": 3,
        # "scalingTypePdf": 3,
        "isLandscapeEnabled":False,#landscape横向，portrait 纵向，若不设置该参数，默认纵向
        "isCssBackgroundEnabled": True,
        "mediaSize": {
            "height_microns": 297000,
            "name": "ISO_A4",
            "width_microns": 210000,
            "custom_display_name": "A4 210 x 297 mm"
        },
    }
 
 
    chrome_options.add_argument('--enable-print-browser')
 
    if headless:
        chrome_options.add_argument('--headless') #headless模式下，浏览器窗口不可见，可提高效率
 
    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': save_root #此处填写你希望文件保存的路径
    }
    chrome_options.add_argument('--kiosk-printing') #静默打印，无需用户点击打印页面的确定按钮
    chrome_options.add_experimental_option('prefs', prefs)
 
 
    driver = webdriver.Chrome(options=chrome_options)
 
    print('-'*100)
    print(f'now: url: {url}')
    driver.get(url)
 
    # 获取当前所有窗口的句柄
    handles = driver.window_handles
    # 切换到最后一个窗口（假设最后一个窗口是要操作的窗口）
    driver.switch_to.window(handles[-1])
 
 
    # 获取当前视口的高度
    viewport_height = driver.execute_script("return window.innerHeight;")
    # 获取滚动条的位置
    current_scroll_position = driver.execute_script("return window.scrollY;")
 
    # 定义滚动的距离和间隔时间
    scroll_distance = 200 # 每次滚动的距离
    scroll_interval = 0.5 # 每次滚动的间隔时间（秒）
 
    # 计算需要滚动的次数
    num_scrolls = int((driver.execute_script("return document.body.scrollHeight;") - current_scroll_position) / scroll_distance)
 
    print('scroll pages...')
    # 循环滚动页面
    for _ in range(num_scrolls):
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
        time.sleep(scroll_interval)
 
    # # 执行 JavaScript 代码，将页面滚动到底部
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # 等待页面加载完成
    # 添加适当的等待时间或条件，确保页面已完全加载
    time.sleep(5)
 
    driver.maximize_window()
    
    #利用js修改网页的title，该title最终就是PDF文件名，
    # 利用js的window.print可以快速调出浏览器打印窗口，避免使用热键ctrl+P
    path = os.path.join(save_root, file_name)
    print(f'save pdf: {path}')
    driver.execute_script(f'document.title="{file_name}";window.print();') 
    driver.close()
 
 
def download_urls(url_list, name_list, save_root):
    for url, name in zip(url_list, name_list):
        print_url_to_pdf(url, save_root, name)
        time.sleep(5)
 
 
 
url_list =[
    'https://mp.weixin.qq.com/s/2m8MrsCxf5boiH4Dzpphrg'
]
name_list = [
    'test333.pdf'
]
save_root = 'D:\\GitHub\\LEARN_LLM\\WeChat\\'
download_urls(url_list, name_list, save_root)