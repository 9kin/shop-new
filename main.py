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


# elasticsearch.indices.delete('items')


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


class Items(Resource):
    def get(self):
        args = parser.parse_args()
        if args["id"] is not None:
            item = (
                session.query(items.Item)
                .filter(items.Item.id == int(args["id"]))
                .first()
            )

            json = item.to_dict(only=(["name", "id", "cost", "count"]))
            img_sql = (
                session.query(images.Image).filter(images.Image.name == item.id).first()
            )
            if img_sql is None:
                json["img"] = "static/not.png"
            else:
                json["img"] = (
                    session.query(images.Image)
                    .filter(images.Image.name == item.id)
                    .first()
                    .path
                )
            if item is not None:
                return jsonify(json)
            else:
                return not_found(404)
        else:
            try:
                item_list = (
                    session.query(items.Item)
                    .filter(items.Item.group == args["path"])
                    .all()
                )
                json_items = {}
                for item in item_list:
                    json_element = item.to_dict(only=(["id", "cost", "count"]))
                    json_items[item.name] = json_element

                    img_sql = (
                        session.query(images.Image)
                        .filter(images.Image.name == item.id)
                        .first()
                    )
                    if img_sql is None:
                        json_items[item.name]["img"] = "static/not.png"
                    else:
                        json_items[item.name]["img"] = (
                            session.query(images.Image)
                            .filter(images.Image.name == item.id)
                            .first()
                            .path
                        )
                    # без limit offset
                    # TODO я не знаю как делать связи между бд

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
                return jsonify(items=json_items, name=path_list)
            except:
                return not_found(404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


class ReForm(FlaskForm):
    regex_field = StringField("regex search", validators=[DataRequired()])
    ini_field = TextAreaField("INI")

    submit = SubmitField("найти")


@app.route("/", methods=["GET", "POST"])
def index():
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


api.add_resource(Items, "/api/items")


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
