from flask import Flask, render_template, request, jsonify, make_response
import json, requests
from flask_restful import reqparse

app = Flask(__name__)


parser = reqparse.RequestParser()
parser.add_argument("path")


@app.route('/items/<string:path>')
def item(path):
    response = requests.get(f'http://localhost:8080/api/items?path={path}')
    if response.status_code == 200:
        return render_template('item.html', data=response.json())
    else:
        return "Error: " + str(response.status_code) 

@app.route('/')
@app.route('/index')
def index():
    with open("categories.json", "rt", encoding="utf8") as f:
        categories = json.loads(f.read())
    return render_template('index.html', categories=categories)


@app.route("/plumbing/<int:id>")
def plumbing(id):
    response = requests.get(f'http://localhost:8080/api/category?path=1.{id}')
    if response.status_code == 200:
        return "OK<br>" + str(response.json())
    else:
        return "Error: " + str(response.status_code)


@app.route("/api/category", methods=['GET'])
def getCategory():
    for _ in range(1000000):
        pass
    path = parser.parse_args()["path"]
    response = requests.get('http://localhost:8080/api/category?path='+path)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return make_response(jsonify({"error code": response.status_code}), response.status_code)


@app.route('/news')
def news():
    with open("news.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    print(news_list)
    return render_template('news.html', news=news_list)


if __name__ == '__main__':
    app.run(port=8000, host='127.0.0.1')