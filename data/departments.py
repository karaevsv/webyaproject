import sqlalchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Department(SqlAlchemyBase):
    __tablename__ = 'departments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    building_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("buildings.id"))
    building = orm.relationship('Building')

    staff = orm.relationship('Staff', back_populates='department')


class DepartmentForm(FlaskForm):
    name = StringField('Название отдела', validators=[DataRequired()])
    building = SelectField('Здание', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Применить')