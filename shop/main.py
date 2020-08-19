import configparser
import json
import os
import time
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
from flask_profiler import Profiler
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

from . import config, ext, search
from .build import elasticsearch, keywords, sql
from .database import Config, Image, Item, User
from .keywords import Keyword, KeywordTable, aslist_cronly

CONFIG = ext.Parser()


import os

# https://stackoverflow.com/a/48040453/13156381
APP_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_PATH = os.path.join(APP_PATH, "templates/")
app = Flask(
    __name__,
    template_folder=TEMPLATE_PATH,
    static_folder=os.path.join(APP_PATH, "static/"),
)
api = Api(app)
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config["JSON_AS_ASCII"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"


profiler = Profiler()

app.config["DEBUG"] = True

app.config["flask_profiler"] = {
    "enabled": app.config["DEBUG"],
    "storage": {"engine": "sqlite"},
    "basicAuth": {"enabled": True, "username": "admin", "password": "admin"},
    "ignore": ["^/static/.*"],
}

profiler = Profiler()  # You can have this in another module
profiler.init_app(app)


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


def extract_items(path):
    items = Item.select().where(Item.group == path)
    if items:
        items = [i for i in items]
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
        return jsonify(items=l, path=items_path(path))
    return not_found(404)


class Items(Resource):
    def get(self, path):
        return extract_items(path)


def search_items(query):
    if query is not None:
        query = search.search(Item, query.lower())
        return jsonify(items={})

        if query is None:
            return jsonify(items={})

        all_items = query.all()

        if all_items is None:
            return not_found(404)

        json_objects = items_sort(
            [item_to_json(item) for item in all_items], args["sortby"]
        )

        return jsonify(items=json_objects)
    return jsonify({"error": "Not found"})


class ReForm(FlaskForm):
    regex_field = StringField("regex search", validators=[DataRequired()])
    ini_field = TextAreaField("INI")

    submit = SubmitField("найти")


@app.route("/ini", methods=["GET", "POST"])
def ini():
    item = session.query(Item).all()
    form = ReForm()
    if form.validate_on_submit():
        regex_field = form.regex_field.data.lower()
        ini_field = form.ini_field.data
        config = configparser.ConfigParser()
        config.read_string(ini_field)

        table = KeywordTable(
            [
                Keyword(keyword, key)
                for key in config["table"]
                for keyword in aslist_cronly(config["table"][key])
            ]
        )

        regex_search = []
        ini_search = []
        for obj in item:
            res = table.contains(obj.name.lower())
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
            "table.html",
            form=form,
            menu=menu_map,
            data=regex_search,
            ini=ini_search,
        )
    return render_template("table.html", form=form, menu=menu_map, data=item)


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
        "item.html", data=search_items(g.search_form.q.data)
    )


def find_item(json, name):
    items = json["items"]
    for item in items:
        if item["name"] == name:
            return item
    return None


@app.route("/items/<string:path>", methods=["GET", "POST"])
def item(path):
    response = extract_items(path)
    if response.status_code != 200:
        return not_found(response.status_code)

    response_json = response.get_json()
    if config.Route().routing(path) is not None:
        curent_class = config.Route().routing(path)
        data = curent_class.table.data
        if data is None:
            data = response_json["items"]
        else:
            data = data.copy()

        for line in data:
            if type(line["cost"]) == str:
                it = find_item(response_json, line["cost"])
                if it is not None:
                    line["cost"] = it["cost"]
                else:
                    line["cost"] = "-"

        table = curent_class.table.table(data)

        return render_template(
            "item_table.html",
            path=response_json["path"],
            table=table,
            md=markdown.markdown(curent_class.text),
        )
    # TODO  md for all items

    return render_template("item.html", data=response_json, form=form)


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


api.add_resource(Items, "/api/items/<string:path>")
# api.add_resource(Search, "/api/search")  TODO
api.add_resource(GoBuild, "/api/gobuild")

if __name__ == "__main__":
    app.run(port=8000)
