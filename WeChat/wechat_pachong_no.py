import pdfkit

path_wk = r'd:\\wkhtmltopdf\\bin\\wkhtmltopdf.exe' #你的wkhtmltopdf安装位置
config = pdfkit.configuration(wkhtmltopdf = path_wk)
url = 'https://mp.weixin.qq.com/s/2m8MrsCxf5boiH4Dzpphrg'   # 你要转的网页链接
pdfkit.from_url(url, r'D:\\GitHub\\LEARN_LLM\\WeChat\\pdfkit_test1.pdf', configuration=config)  # 你要保存到的路径及pdf名字
