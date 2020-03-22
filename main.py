from flask import Flask, url_for, request, render_template
import data.db_session as db
from data.__all_models import *

db.global_init('db/items.sqlite')
session = db.create_session()
item = session.query(items.Item).all()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

menu = list(map(str.strip, open('menu.txt', 'r').readlines()))

menu_map = {'others': 'x'}
for el in menu:
    ind = el.find(' ')
    menu_map[el[:ind]] = el[ind + 1:]

@app.route('/')
def index():
    return render_template('table.html', data=item, menu=menu_map)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')