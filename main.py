from flask import Flask, render_template
import json, requests

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    with open("categories.json", "rt", encoding="utf8") as f:
        categories = json.loads(f.read())
    return render_template('index.html', categories=categories)


@app.route("/plumbing/<int:id>")
def plumbing(id):
	response = requests.get('http://localhost:8080/api/category?path=1.'+str(id))
	if response.status_code == 200:
		return "OK<br>" + str(response.json())
	else:
		return "Error: " + str(response.status_code)


@app.route('/news')
def news():
    with open("news.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    print(news_list)
    return render_template('news.html', news=news_list)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')