from flask import Flask, url_for, request, render_template, jsonify, make_response
from flask_restful import reqparse, abort, Api, Resource

import data.db_session as db
from data.__all_models import *

db.global_init('db/items.sqlite')
session = db.create_session()
item = session.query(items.Item).all()

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

menu = list(map(str.strip, open('menu.txt', 'r').readlines()))

menu_map = {'others': 'x'}
for el in menu:
    ind = el.find(' ')
    menu_map[el[:ind]] = el[ind + 1:]


parser = reqparse.RequestParser()
parser.add_argument('id')
parser.add_argument('limit')
parser.add_argument('offset')
parser.add_argument('path')


class Items(Resource):
    def get(self):
        args = parser.parse_args()
        if args['id'] is not None:
            return jsonify(item[int(args['id'])].to_dict())
        else:
            item_list = session.query(items.Item).filter(
                items.Item.group == args['path']).all()
            json_items = {}
            for item in item_list:
                json_element = item.to_dict(only=(['id', 'cost', 'count']))
                json_items[item.name] = json_element
                json_items[item.name]['img'] = session.query(
                    images.Image).filter(images.Image.id == item.id).one().path
                # без limit offset
                # TODO я не знаю как делать связи между бд
            return jsonify(json_items)


class Category(Resource):
    def get(self):
        args = parser.parse_args()
        if args['path'] is not None:
            json = {}
            for key in menu_map:
                print(key)
                if key.startswith(args['path'] + '.'):
                    json[key] = menu_map[key]
            return jsonify(categories=json)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def index():
    return render_template('table.html', data=item, menu=menu_map)


api.add_resource(Items, '/api/items')
api.add_resource(Category, '/api/category')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
