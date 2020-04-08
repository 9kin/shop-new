from sqlalchemy_serializer import SerializerMixin
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Image(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "images"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    path = sqlalchemy.Column(sqlalchemy.String, default="not.png")
