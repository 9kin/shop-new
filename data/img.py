import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Item(SqlAlchemyBase):
    __tablename__ = 'items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    group = sqlalchemy.Column(sqlalchemy.String, default="others")

    def __repr__(self):
        return f'{self.name} {self.cost}'

