from flask_table import Table, Col, create_table, BoolCol
import tabels.all as tabels
import config
import markdown

import configparser
import json
import os

import flask_admin as admin
import flask_login as login
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
from flask_admin.contrib import sqla
from flask_restful import Api, Resource, reqparse
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

import data.db_session as db
import ext
import search
from build import elasticsearch, keywords, sql
from data.images import Image
from data.items import Item
from data.users import User
from keywords import Keyword, KeywordTable, aslist_cronly

CONFIG = ext.Parser()

db.global_init("db/items.sqlite")

app = Flask(__name__)
api = Api(app)
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config["JSON_AS_ASCII"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"


class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired("File was empty!")])

    file = FileField(
        validators=[
            FileRequired("File was empty!"),
            FileAllowed(["txt"], "txt only!"),
        ]
    )
    submit = SubmitField("Загрузить")


class Build(BaseView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = UploadForm()
        if form.validate_on_submit():
            data = form.file.data
            data.save(CONFIG.remains)
        return self.render("/admin/build.html", form=form)


class LoginForm(form.Form):
    login = StringField()
    password = PasswordField()

    def validate_login(self, field):
        cur_user = self.get_user()
        if cur_user is None:
            raise validators.ValidationError("Invalid user")
        if not check_password_hash(cur_user.password, self.password.data):
            raise validators.ValidationError("Invalid password")

    def get_user(self):
        session = db.create_session()
        return session.query(User).filter_by(login=self.login.data).first()


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        session = db.create_session()
        return session.query(User).get(user_id)


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


init_login()


admin = admin.Admin(
    app, "admin", index_view=MyAdminIndexView(), base_template="my_master.html"
)


def create_admin():
    session = db.create_session()
    if session.query(User).filter_by(login="admin").count() < 1:
        user = User(login="admin", password=generate_password_hash("admin"))
        session.add(user)
        session.commit()


create_admin()

session = db.create_session()
admin.add_view(MyModelView(Item, session))
admin.add_view(MyModelView(Image, session))
admin.add_view(MyModelView(User, session))
admin.add_view(Build(name="Build"))


menu = list(map(str.strip, open("menu.txt", "r").readlines()))

menu_map = {"others": "x"}
for el in menu:
    ind = el.find(" ")
    menu_map[el[:ind]] = el[ind + 1 :]


parser = reqparse.RequestParser()
parser.add_argument("id")
parser.add_argument("path")
parser.add_argument("sortby")

parser.add_argument("path")

parser.add_argument("q")

parser.add_argument("build_args")


def item_to_json(item):
    json_obj = {}
    json_obj = item.to_dict(only=(["id", "cost", "count"]))
    img_sql = session.query(Image).filter(Image.name == item.name).first()
    if img_sql is None:
        json_obj["img"] = "not.png"
    else:
        json_obj["img"] = img_sql.path
    json_obj["name"] = item.name
    return json_obj


"""
_d - по убыванию (reverse=True)
_i - по возрастанию (reverse=False)


pd - по убыванию цены
pi - по возрастанию цены

cd - по убыванию количества
ci - по возрастанию количества

a(d/i) - по алфавиту

"""


def items_sort(items, sortby):
    scheme = {
        "pd": (lambda x: x["cost"], True),
        "pi": (lambda x: x["cost"], False),
        "cd": (lambda x: x["count"], True),
        "ci": (lambda x: x["count"], False),
        "ad": (lambda x: x["name"], True),
        "ai": (lambda x: x["name"], False),
        None: (lambda x: x["cost"], False),
    }
    cur = scheme[sortby]
    items.sort(key=cur[0], reverse=cur[1])
    return items


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


class Items(Resource):
    def get(self):
        args = parser.parse_args()
        if args["id"] is not None:
            item = (
                session.query(Item).filter(Item.id == int(args["id"])).first()
            )
            if item is None:
                return not_found(404)
            return jsonify(
                item=item_to_json(item), path=items_path(item.group)
            )

        elif args["path"] is not None:
            all_items = (
                session.query(Item).filter(Item.group == args["path"]).all()
            )

            if all_items is None:
                return not_found(404)

            json_objects = items_sort(
                [item_to_json(item) for item in all_items], args["sortby"]
            )

            return jsonify(items=json_objects, path=items_path(args["path"]))
        return not_found(404)


class Search(Resource):
    def get(self):
        args = parser.parse_args()
        if args["q"] is not None:
            query = search.search(Item, args["q"].lower(), session)
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


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), error)


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
        print(regex_field)
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
    args = parser.parse_args()
    if args["sortby"] is None:
        args["sortby"] = "pi"
    args["q"] = g.search_form.q.data

    if not g.search_form.validate():
        return redirect(url_for("."))
    response = requests.get(f"{request.host_url}/api/search", params=args)
    return render_template(
        "item.html", data=response.json(), sortby=args["sortby"]
    )


api.add_resource(Items, "/api/items")
api.add_resource(Search, "/api/search")
api.add_resource(GoBuild, "/api/gobuild")


def find_item(json, name):
    items = json["items"]
    for item in items:
        if item["name"] == name:
            return item
    return None


@app.route("/items/<string:path>", methods=["GET", "POST"])
def item(path):
    args = parser.parse_args()
    args["path"] = path
    if args["sortby"] is None:
        args["sortby"] = "pi"

    response = requests.get(f"{request.host_url}/api/items", params=args)
    if response.status_code == 200:

        if config.Route().routing(path) is not None:
            response_json = response.json()

            curent_class = config.Route().routing(path)
            if type(curent_class.tabel) == bool:
                curent_class.tabel = response_json["items"]

            tabel = curent_class.tabel.copy()

            for line in tabel:
                if type(line["cost"]) == str:
                    line["cost"] = find_item(response_json, line["cost"])[
                        "cost"
                    ]

            table = curent_class.tabel_cls(tabel)
            return render_template(
                "item_table.html",
                path=response_json["path"],
                sortby=args["sortby"],
                table=table,
                md=markdown.markdown(curent_class.text),
            )

        return render_template(
            "item.html", data=response.json(), form=form, sortby=args["sortby"]
        )
    return not_found(response.status_code)


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


if __name__ == "__main__":
    app.run(port=8000, debug=False)
