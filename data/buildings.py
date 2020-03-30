import datetime
import sqlalchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Building(SqlAlchemyBase):
    __tablename__ = 'buildings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    departments = orm.relation('Department', back_populates='building')


class BuildingsForm(FlaskForm):
    name = StringField('Название здания', validators=[DataRequired()])
    submit = SubmitField('Применить')