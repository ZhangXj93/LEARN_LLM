from flask import Flask, render_template, request, jsonify
from http import HTTPStatus
from openai import OpenAI
import mechanicalsoup
from bs4 import BeautifulSoup
from flask_cors import CORS
from urllib.parse import urlparse, parse_qs, quote
app = Flask(__name__)
client = OpenAI()

CORS(app)

history = []
def crawl_pages(query_text, page_num=2):
    browser = mechanicalsoup.Browser()
    query_text_encoded = quote(query_text)
    results = []
    for page_index in range(1, page_num+1):
        url = f"https://search.cctv.com/search.php?qtext={query_text_encoded}&type=web&page={page_index}"
        page = browser.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        web_content_links = soup.find_all('a', id=lambda x: x and x.startswith('web_content_'))
        for i, link in enumerate(web_content_links):
            target_page = parse_qs(urlparse(link['href']).query).get('targetpage', [None])[0]
            results.append({'title': link.text, 'url': target_page})
    return results

def get_openai_chat_completion(messages, temperature, model = "gpt-3.5-turbo-1106"):
    response = client.chat.completions.create(
        model = model,
        messages = messages,
        temperature = temperature,
    )
    return response

def generate_text(prompt, temperature=0.5):
    messages = [
        {
            "role": "user",
            "content": prompt,
        }   
    ]
    response = get_openai_chat_completion(messages = messages, temperature=temperature)
    generated_text = response.choices[0].message.content
    history.append({"user": prompt, "bot": generated_text})  # 将用户输入和模型输出添加到历史记录中
    return {"status": "success", "response": generated_text}

@app.route('/', methods=['GET'])
def index():
    chat_history = history
    return render_template('ai_search.html', history=chat_history)

@app.route('/generate-text', methods=['POST'])
def generate_text_api():
    prompt = request.json['prompt']
    result = generate_text(prompt)
    return jsonify(result)

@app.route('/clear', methods=['POST'])
def clear():
    global history
    history = []
    return '', HTTPStatus.NO_CONTENT

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
    elif request.method == 'GET':
        keyword = request.args.get('keyword', '')
    else:
        keyword = ''
    
    results = crawl_pages(keyword)
    output = ""
    for result in results:
     output += f"<li><a id='myID' href='javascript:void(0);' onclick='handleLinkClick(\"{result['url']}\")'>{result['title']}</a></li><br>"
    return output

@app.route('/page_content')
def page_content():
    url = request.args.get('url', '')
    if not url:
        return '缺少 url 参数'
    browser = mechanicalsoup.Browser()
    page = browser.get(url)
    page.encoding = 'utf-8'  # 指定页面的编码为 utf-8
    soup = BeautifulSoup(page.text, 'html.parser')
    all_text = ''
    all_images = []

    # 获取页面中所有文本内容
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span']):
        all_text += element.get_text() + ' '

    # 获取页面中所有图片链接
    for img in soup.find_all('img'):
        img_src = img.get('src')
        if img_src:
            all_images.append("https:"+img_src)

    return f"文本内容: {all_text}<br>图片链接: {', '.join(all_images)}"

if __name__ == '__main__':
    app.run(debug=True)