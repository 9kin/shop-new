import json
from flask import g
import requests
import search
from keywords import Keyword, KeywordTable, aslist_cronly
import configparser
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import re
from flask import Flask, url_for, request, render_template, jsonify, make_response
from flask_restful import reqparse, abort, Api, Resource


from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextField,
    TextAreaField,
)
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed

import data.db_session as db
from data.__all_models import *


import os
from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from werkzeug.security import generate_password_hash, check_password_hash

from elasticsearch import Elasticsearch

db.global_init("db/items.sqlite")
session = db.create_session()

app = Flask(__name__)
api = Api(app)
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config["JSON_AS_ASCII"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"


class LoginForm(form.Form):
    login = fields.StringField()
    password = fields.PasswordField()

    def validate_login(self, field):
        user = self.get_user()
        if user is None:
            raise validators.ValidationError("Invalid user")
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError("Invalid password")

    def get_user(self):
        return session.query(users.User).filter_by(login=self.login.data).first()


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return session.query(users.User).get(user_id)


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated


class MyAdminIndexView(admin.AdminIndexView):
    @expose("/")
    def index(self):
        if not login.current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(MyAdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)
        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        self._template_args["form"] = form
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))


init_login()

admin = admin.Admin(
    app, "admin", index_view=MyAdminIndexView(), base_template="my_master.html"
)


if session.query(users.User).filter_by(login="admin").count() < 1:
    user = users.User(login="admin", password=generate_password_hash("admin"))
    session.add(user)
    session.commit()


admin.add_view(MyModelView(items.Item, session))
admin.add_view(MyModelView(images.Image, session))
admin.add_view(MyModelView(users.User, session))


menu = list(map(str.strip, open("menu.txt", "r").readlines()))

menu_map = {"others": "x"}
for el in menu:
    ind = el.find(" ")
    menu_map[el[:ind]] = el[ind + 1 :]


parser = reqparse.RequestParser()
parser.add_argument("id")
parser.add_argument("limit")
parser.add_argument("offset")
parser.add_argument("path")
parser.add_argument("q")
parser.add_argument("path")


def item_to_json(item):
    json = {}
    json[item.name] = item.to_dict(only=(["id", "cost", "count"]))
    img_sql = session.query(images.Image).filter(images.Image.name == item.name).first()
    if img_sql is None:
        json[item.name]["img"] = "not.png"
    else:
        json[item.name]["img"] = img_sql.path
    return json


class Items(Resource):
    def get(self):
        args = parser.parse_args()
        if args["id"] is not None:
            item = (
                session.query(items.Item)
                .filter(items.Item.id == int(args["id"]))
                .first()
            )

            path_list = []
            prev = ""
            first = True
            for i in item.group.split("."):
                if first:
                    first = False
                else:
                    prev += "."
                prev += str(i)
                path_list.append(menu_map[prev])
            if item is not None:
                return jsonify(item=item_to_json(item), path=path_list)
            else:
                return not_found(404)
        else:
            try:
                all_items = (
                    session.query(items.Item)
                    .filter(items.Item.group == args["path"])
                    .all()
                )
                json = {}
                for item in all_items:
                    json[item.name] = item_to_json(item)[item.name]

                path_list = []
                prev = ""
                first = True
                for i in args["path"].split("."):
                    if first:
                        first = False
                    else:
                        prev += "."
                    prev += str(i)
                    path_list.append(menu_map[prev])
                return jsonify(items=json, path=path_list)
            except:
                return not_found(404)


class Search(Resource):
    def get(self):
        args = parser.parse_args()
        if args["q"] is not None:
            query = search.search(items.Item, args["q"], session)
            if query is None:
                return jsonify(items={})
            json = {}
            for item in query.all():
                json[item.name] = item_to_json(item)[item.name]
            return jsonify(items=json)
        return jsonify({"error": "q Not found"})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


class ReForm(FlaskForm):
    regex_field = StringField("regex search", validators=[DataRequired()])
    ini_field = TextAreaField("INI")

    submit = SubmitField("найти")


@app.route("/ini", methods=["GET", "POST"])
def ini():
    item = session.query(items.Item).all()
    form = ReForm()
    if form.validate_on_submit():
        regex_field = form.regex_field.data
        ini_field = form.ini_field.data
        config = configparser.ConfigParser()
        config.read_string(ini_field)

        TABLE = KeywordTable(
            [
                Keyword(keyword, key)
                for key in config["table"]
                for keyword in aslist_cronly(config["table"][key])
            ]
        )

        regex_search = []
        ini_search = []
        for obj in item:
            res = TABLE.contains(obj.name.lower())
            if res != False:
                if obj == regex_field:
                    obj.full_match = True
                    regex_search.append(obj)
                else:
                    obj.full_match = False
                    ini_search.append(obj)
            elif obj == regex_field:
                obj.full_match = False
                regex_search.append(obj)
            else:
                obj.full_match = False
        return render_template(
            "table.html", form=form, menu=menu_map, data=regex_search, ini=ini_search
        )
    return render_template("table.html", form=form, menu=menu_map, data=item)


class Category(Resource):
    def get(self):
        args = parser.parse_args()
        if args["path"] == "":
            return jsonify(categories=menu_map, name="")
        elif args["path"] is not None:
            json = {}
            i = 1

            while f'{args["path"]}.{i}' in menu_map:
                json[i] = menu_map[f'{args["path"]}.{i}']
                i += 1
            i -= 1
            path_list = []
            prev = ""
            first = True
            for i in args["path"].split("."):
                if first:
                    first = False
                else:
                    prev += "."
                prev += str(i)
                if prev in menu_map:
                    path_list.append(menu_map[prev])
                else:
                    return not_found(404)

            return jsonify(categories=json, name=path_list)


class SearchForm(FlaskForm):
    q = StringField("Search", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)


@app.before_request
def before_request():
    g.search_form = SearchForm()


@app.route("/search")
def search_route():
    if not g.search_form.validate():
        return redirect(url_for("."))
    response = requests.get(
        f"http://localhost:8000/api/search?q={g.search_form.q.data}"
    )
    return render_template("item.html", data=response.json())


api.add_resource(Items, "/api/items")
api.add_resource(Category, "/api/category")
api.add_resource(Search, "/api/search")


@app.route("/items/<string:path>")
def item(path):
    response = requests.get(f"http://localhost:8000/api/items?path={path}")
    if response.status_code == 200:
        if path.startswith("1.2"):
            return render_template("item_table.html", data=response.json())
        return render_template("item.html", data=response.json())
    else:
        return "Error: " + str(response.status_code)


@app.route("/")
@app.route("/index")
def index():
    with open("categories.json", "rt", encoding="utf8") as f:
        categories = json.loads(f.read())
    return render_template("index.html", categories=categories)


@app.route("/api/category", methods=["GET"])
def getCategory():
    for _ in range(1000000):
        pass
    path = parser.parse_args()["path"]
    response = requests.get("http://localhost:8000/api/category?path=" + path)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return make_response(
            jsonify({"error code": response.status_code}), response.status_code
        )


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(port=8000, host="127.0.0.1")
