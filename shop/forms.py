from flask import request
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

from .database import User


class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired("File was empty!")])

    file = FileField(
        validators=[
            FileRequired("File was empty!"),
            FileAllowed(["txt"], "txt only!"),
        ]
    )
    submit = SubmitField("Загрузить")


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


class SearchForm(FlaskForm):
    q = StringField("поиск товара", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)
