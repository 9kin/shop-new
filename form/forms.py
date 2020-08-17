from wtforms.validators import DataRequired, Optional

from wtforms import (
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    form,
    validators,
)

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired


class UploadForm(FlaskForm):
    file = FileField(validators=[FileRequired("File was empty!")])

    file = FileField(
        validators=[
            FileRequired("File was empty!"),
            FileAllowed(["txt"], "txt only!"),
        ]
    )
    submit = SubmitField("Загрузить")
