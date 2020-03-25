from sqlalchemy_serializer import SerializerMixin
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Image(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "images"

    name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    path = sqlalchemy.Column(sqlalchemy.String, default="static/img/not.png")
