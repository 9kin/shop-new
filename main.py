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
    url_for,
    send_from_directory,
)
from flask_admin import expose, helpers
from flask_admin.contrib import sqla
from flask_restful import Api, Resource, reqparse
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import (
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
    form,
    validators,
)
from wtforms.validators import DataRequired

import data.db_session as db
import ext
import search
from data.images import Image
from data.items import Item
from data.users import User
from data.build import Build
from keywords import Keyword, KeywordTable, aslist_cronly

config = ext.Parser()

db.global_init("db/items.sqlite")


app = Flask(__name__)
api = Api(app)
app.config["JSON_SORT_KEYS"] = False
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config["JSON_AS_ASCII"] = False
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"


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
#admin.add_view(MyModelView(Build, session))
admin.add_view(Build(name='Build'))


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
parser.add_argument("build_args")


def item_to_json(item):
    json_obj = {}
    json_obj[item.name] = item.to_dict(only=(["id", "cost", "count"]))
    img_sql = session.query(Image).filter(Image.name == item.name).first()
    if img_sql is None:
        json_obj[item.name]["img"] = "not.png"
    else:
        json_obj[item.name]["img"] = img_sql.path
    return json_obj


class Items(Resource):
    def get(self):
        args = parser.parse_args()
        if args["id"] is not None:
            item = (
                session.query(Item).filter(Item.id == int(args["id"])).first()
            )
            if item is None:
                return not_found(404)
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
            return not_found(404)

        all_items = (
            session.query(Item).filter(Item.group == args["path"]).all()
        )
        if all_items is None:
            return not_found(404)
        json_objects = {}
        for item in all_items:
            json_objects[item.name] = item_to_json(item)[item.name]

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
        return jsonify(items=json_objects, path=path_list)


class Search(Resource):
    def get(self):
        args = parser.parse_args()
        if args["q"] is not None:
            query = search.search(Item, args["q"], session)
            if query is None:
                return jsonify(items={})
            json = {}
            for item in query.all():
                json[item.name] = item_to_json(item)[item.name]
            return jsonify(items=json)
        return jsonify({"error": "q Not found"})


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
        regex_field = form.regex_field.data
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
            if not res:
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


class Category(Resource):
    def get(self):
        args = parser.parse_args()
        if args["path"] == "":
            return jsonify(categories=menu_map, name="")
        elif args["path"] is not None:
            json_obj = {}
            i = 1

            while f'{args["path"]}.{i}' in menu_map:
                json_obj[i] = menu_map[f'{args["path"]}.{i}']
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
            return jsonify(categories=json_obj, name=path_list)
        return not_found(404)


class GoBuild(Resource):
    def get(self):
        args = parser.parse_args()
        args = args["build_args"]
        if args is None:
            return "args not found"
        code = os.system("python3 build.py " + args)
        if code == 0:
            return "OK"
        else:
            return code


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
        f"http://localhost:{config.port}/api/search?q={g.search_form.q.data}"
    )
    return render_template("item.html", data=response.json())


api.add_resource(Items, "/api/items")
api.add_resource(Category, "/api/category")
api.add_resource(Search, "/api/search")
api.add_resource(GoBuild, "/api/gobuild")


@app.route("/items/<string:path>")
def item(path):
    response = requests.get(
        f"http://localhost:{config.port}/api/items?path={path}"
    )
    if response.status_code == 200:
        if path.startswith("1.2"):
            return render_template("item_table.html", data=response.json())
        return render_template("item.html", data=response.json())
    return not_found(response.status_code)


@app.route("/")
@app.route("/index")
def index():
    with open("categories.json", "rt", encoding="utf8") as file:
        categories = json.loads(file.read())
    return render_template("index.html", categories=categories)


@app.route("/api/category", methods=["GET"])
def get_category():
    for _ in range(1000000):
        pass
    path = parser.parse_args()["path"]
    response = requests.get(
        f"http://localhost:{config.port}/api/category?path=" + path
    )

    if response.status_code == 200:
        return jsonify(response.json())
    return make_response(
        jsonify({"error code": response.status_code}), response.status_code
    )


@app.route("/contacts")
def contacts():
    return render_template("contacts.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.run(port=config.port, host="0.0.0.0")
