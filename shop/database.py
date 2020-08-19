import re

from flask_login import UserMixin
from peewee import (
    CharField,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    SqliteDatabase,
    TextField,
    chunked,
)

db = SqliteDatabase("db/items.sqlite", check_same_thread=False)


class BaseModel(Model):
    class Meta:
        database = db


class Item(BaseModel):
    id = IntegerField(primary_key=True)

    name = TextField()
    cost = FloatField()
    count = IntegerField()
    group = TextField(default="others")
    img = "not.png"

    full_match = False

    __tablename__ = "item"
    __searchable__ = ["name"]

    def __eq__(self, other):
        return re.fullmatch(other, self.name.lower())


class Image(BaseModel):
    name = ForeignKeyField(Item, backref="images")
    path = TextField(default="not.png")


class User(BaseModel, UserMixin):

    id = IntegerField(primary_key=True)
    login = TextField(unique=True)
    password = TextField()


class Config(BaseModel):

    name = TextField(unique=True)
    config = TextField()
