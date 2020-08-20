import configparser
import json
import os
import time
from copy import deepcopy
from pprint import pprint

import flask_admin as admin
import flask_login as login
import markdown
import requests
from flask import (
    Flask,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_admin import BaseView, expose, helpers
from flask_admin.contrib.peewee import ModelView
from flask_restful import Api, Resource, reqparse
from flask_table import BoolCol, Col, Table, create_table
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import (
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    form,
    validators,
)
from wtforms.validators import DataRequired, Optional

from form.forms import UploadForm

from . import ext, search
from .build import elasticsearch, keywords, sql
from .database import Config, Image, Item, User
from .ext import Route, get_table
from .keywords import Keyword, KeywordTable, aslist_cronly

CONFIG = ext.Parser()


import os

# https://stackoverflow.com/a/48040453/13156381
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    static_url_path="",
    template_folder=os.path.join(APP_PATH, "templates/"),
    static_folder=os.path.join(APP_PATH, "static/"),
)
api = Api(app)
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config["JSON_AS_ASCII"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"


class Build(BaseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = UploadForm()
        if form.validate_on_submit():
            data = form.file.data
            data.save(CONFIG.remains)
            # TODO
        return self.render("/admin/build.html", form=form)


class LoginForm(FlaskForm):
    login = StringField()
    password = PasswordField()

    def validate_login(self, field):
        cur_user = self.get_user()
        if cur_user is None:
            raise validators.ValidationError("Invalid user")
        if not check_password_hash(cur_user.password, self.password.data):
            raise validators.ValidationError("Invalid password")

    def get_user(self):
        return User.get(User.login == self.login.data)


login_manager = login.LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(User.id == user_id)


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
            cur_user = form.get_user()
            login.login_user(cur_user)
        if login.current_user.is_authenticated:
            return redirect(url_for(".index"))
        self._template_args["form"] = form
        return super(MyAdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        login.logout_user()
        return redirect(url_for(".index"))


admin = admin.Admin(
    app, "admin", index_view=MyAdminIndexView(), base_template="my_master.html"
)


def create_admin():
    is_admin = User.select().where(User.login == "admin").count() == 1
    if not is_admin:
        User.create(login="admin", password=generate_password_hash("admin"))


create_admin()


class MyModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated


admin.add_view(MyModelView(Item))
admin.add_view(MyModelView(Image))
admin.add_view(MyModelView(User))
admin.add_view(MyModelView(Config))
admin.add_view(Build(name="Build"))


menu = list(map(str.strip, open("shop/menu.txt", "r").readlines()))

menu_map = {"others": "x"}
for el in menu:
    ind = el.find(" ")
    menu_map[el[:ind]] = el[ind + 1 :]


parser = reqparse.RequestParser()
parser.add_argument("id")
parser.add_argument("path")

parser.add_argument("q")

parser.add_argument("build_args")


s = 0


def items_path(path):
    path_list = []
    prev = ""
    try:
        for i in enumerate(path.split(".")):
            if i[0] != 0:
                prev += "."
            prev += str(i[1])
            path_list.append(menu_map[prev])
    except:
        path_list = []
    return path_list


# ext TODO
def validate_path(path: str):
    # SQL INJECTION
    for char in path:
        if not (char.isdigit() or char == "."):
            return False
    return True


#  TODO ext
def items2json(items):
    m = {item.id: item for item in items}
    imgs = Image.select().where(Image.name.in_(items))
    for i in imgs:
        m[i.name_id].img = i.path
    l = []
    for key in m:
        item = m[key]
        l.append(
            {
                "name": item.name,
                "count": item.count,
                "cost": item.cost,
                "img": item.img,
                "id": item.id,
            }
        )
    l.sort(key=lambda x: x["cost"])
    return l


def extract_items(path: str):
    items = Item.select().where(Item.group == path)
    if items:
        return items2json([i for i in items])
    return []


def search_items(query):
    if query is not None:
        items = search.search("items", Item, query.lower())
        return items2json(items)
    return []


class GoBuild(Resource):
    def get(self):
        args = parser.parse_args()
        args = args["build_args"]
        if args is None:
            return "args not found"
        try:
            if args == "key":
                keywords()
            elif args == "search":
                elasticsearch()
            elif args == "sql":
                sql()
            return "ok"
        except:
            return "error"


class SearchForm(FlaskForm):
    q = StringField("поиск товара", validators=[DataRequired()])

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
    return render_template(
        "item.html", items=search_items(g.search_form.q.data)
    )


def find_item(json, name):
    items = json["items"]
    for item in items:
        if item["name"] == name:
            return item
    return None


@app.route("/items/<string:path>", methods=["GET", "POST"])
def item(path):
    if not validate_path(path):
        return not_found(404)
    items = extract_items(path)
    if "table" in Route().routing(path):
        curent = Route().routing(path).copy()
        table = get_table(curent["table"])
        data = table.data
        if data is None:
            data = items
        else:
            data = deepcopy(data)
            names = []
            for item in data:
                names.append(item["cost"])
            m = {}
            for item in Item.select().where(Item.name.in_(names)):
                m[item.name] = item.cost
            for item in data:
                item["cost"] = m[item["cost"]]
        if "md" in curent:
            md = markdown.markdown(curent["md"])
        else:
            md = ""
        return render_template(
            "item_table.html",
            path=items_path(path),
            table=table.table(data),
            md=md,
        )
    # TODO  md for all items
    return render_template("item.html", items=items, path=items_path(path))


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static", "img"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/")
@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/stock")
def stock():
    return render_template("stock.html")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


# api.add_resource(Items, "/api/items/<string:path>")
# api.add_resource(Search, "/api/search")  TODO
api.add_resource(GoBuild, "/api/gobuild")


def main():
    app.run(port=8000)


if __name__ == "__main__":
    main()
