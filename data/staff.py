import sqlalchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, RadioField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Staff(SqlAlchemyBase):
    __tablename__ = 'staff'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_male = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    department_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('departments.id'))
    department = orm.relation('Department')


class StaffForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    is_male = RadioField('Пол', choices=[('1', 'Мужской'), ('0', 'Женский')], default='1')
    email = EmailField('E-mail', validators=[DataRequired()])
    department = SelectField('Отдел', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Применить')