from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
import os
from flask_restful import abort

from data import db_session
from data.users import User, LoginForm
from data.staff import Staff, StaffForm
from data.departments import Department, DepartmentForm
from data.buildings import Building, BuildingsForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/base.sqlite")

    @login_manager.user_loader
    def load_user(user_id):
        session = db_session.create_session()
        return session.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.login == form.login.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return render_template("index.html", title='Главное меню')
        else:
            return redirect("/login")

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.route('/staff')
    @login_required
    def staff():
        session = db_session.create_session()
        staff = session.query(Staff).all()
        return render_template("staff.html", title='Список сотрудников', staff=staff)

    @app.route('/staff_edit', methods=['GET', 'POST'])
    @login_required
    def add_staff():
        session = db_session.create_session()
        form = StaffForm()
        if form.validate_on_submit():
            staff = Staff()
            staff.name = form.name.data
            staff.surname = form.surname.data
            staff.department_id = form.department.data[0]
            staff.email = form.email
            staff.is_male = bool(form.is_male.data)
            # staff.photo = form.photo.data
            session.add(staff)
            session.commit()
            return redirect('/staff')
        form.department.choices = [(x.id, x.name) for x in session.query(Department).all()]
        return render_template('staff_edit.html', title='Добавление сотрудника',
                               form=form)

    @app.route('/buildings')
    @login_required
    def buildings():
        session = db_session.create_session()
        buildings = session.query(Building).all()
        return render_template("buildings.html", title='Список зданий', buildings=buildings)

    @app.route('/building_edit', methods=['GET', 'POST'])
    @login_required
    def building_add():
        session = db_session.create_session()
        form = BuildingsForm()
        if form.validate_on_submit():
            building = Building()
            building.name = form.name.data
            session.add(building)
            session.commit()
            return redirect('/buildings')
        return render_template('building_edit.html', title='Добавление здания',
                               form=form)

    @app.route('/building_edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def building_edit(id):
        session = db_session.create_session()
        form = BuildingsForm()
        building = session.query(Building).filter(Building.id == id).first()
        if not building:
            abort(404)

        if request.method == "GET":
            form.name.data = building.name

        if form.validate_on_submit():
            building.name = form.name.data
            session.commit()
            return redirect('/buildings')
        return render_template('building_edit.html', title='Редактирование здания',
                               form=form)

    @app.route('/building_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def building_delete(id):
        session = db_session.create_session()
        building = session.query(Building).filter(Building.id == id).first()
        if building:
            session.delete(building)
            session.commit()
        else:
            abort(404)
        return redirect('/buildings')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
