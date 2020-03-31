from flask import Flask, render_template, redirect, request, flash
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
    def staff_add():
        session = db_session.create_session()
        form = StaffForm()
        form.department.choices = [(x.id, x.name) for x in session.query(Department).all()]
        if form.department.choices:
            form.department.default = form.department.choices[0]

        if form.validate_on_submit():
            staff = Staff()
            staff.name = form.name.data
            staff.surname = form.surname.data
            staff.department_id = form.department.data
            staff.email = form.email.data
            staff.is_male = True if form.is_male.data == '1' else False
            session.add(staff)
            session.commit()
            return redirect('/staff')

        return render_template('staff_edit.html', title='Добавление сотрудника',
                               form=form)

    @app.route('/staff_edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def staff_edit(id):
        session = db_session.create_session()

        staff = session.query(Staff).filter(Staff.id == id).first()
        if not staff:
            abort(404)

        form = StaffForm()
        form.department.choices = [(x.id, x.name) for x in session.query(Department).all()]
        if form.department.choices:
            form.department.default = form.department.choices[0]

        if request.method == "GET":
            form.name.data = staff.name
            form.surname.data = staff.surname
            form.email.data = staff.email
            form.is_male.data = '1' if staff.is_male else '0'
            form.department.data = staff.department.id

        if form.validate_on_submit():
            staff.name = form.name.data
            staff.surname = form.surname.data
            staff.department_id = form.department.data
            staff.email = form.email.data
            staff.is_male = True if form.is_male.data == '1' else False
            session.commit()
            return redirect('/staff')

        return render_template('staff_edit.html', title='Добавление сотрудника',
                               form=form)

    @app.route('/staff_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def staff_delete(id):
        session = db_session.create_session()

        staff = session.query(Staff).filter(Staff.id == id).first()
        if staff:
            session.delete(staff)
            session.commit()
        else:
            abort(404)
        return redirect('/staff')

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
            if building.departments:
                flash('Нельзя удалить здание, в котором есть отделы.', 'error')
            else:
                session.delete(building)
                session.commit()
        else:
            abort(404)
        return redirect('/buildings')

    @app.route('/departments')
    @login_required
    def departments():
        session = db_session.create_session()
        departments = session.query(Department).all()
        return render_template("departments.html", title='Список отделов', departments=departments)

    @app.route('/department_edit', methods=['GET', 'POST'])
    @login_required
    def department_add():
        session = db_session.create_session()
        form = DepartmentForm()
        form.building.choices = [(x.id, x.name) for x in session.query(Building).all()]
        if form.building.choices:
            form.building.default = form.building.choices[0]
        if form.validate_on_submit():
            department = Department()
            department.name = form.name.data
            department.building_id = form.building.data
            session.add(department)
            session.commit()
            return redirect('/departments')
        return render_template('department_edit.html', title='Добавление отдела',
                               form=form)

    @app.route('/department_edit/<int:id>', methods=['GET', 'POST'])
    @login_required
    def department_edit(id):
        session = db_session.create_session()
        form = DepartmentForm()
        form.building.choices = [(x.id, x.name) for x in session.query(Building).all()]
        department = session.query(Department).filter(Department.id == id).first()
        if not department:
            abort(404)

        if request.method == "GET":
            form.name.data = department.name
            form.building.data = department.building.id

        if form.validate_on_submit():
            department.name = form.name.data
            department.building_id = form.building.data
            session.commit()
            return redirect('/departments')

        return render_template('department_edit.html', title='Редактирование отдела',
                               form=form)

    @app.route('/department_delete/<int:id>', methods=['GET', 'POST'])
    @login_required
    def department_delete(id):
        session = db_session.create_session()
        department = session.query(Department).filter(Department.id == id).first()

        if department:
            if department.staff:
                flash('Нельзя удалить отдел, в котором есть сотрудники.', 'error')
            else:
                session.delete(department)
                session.commit()
        else:
            abort(404)
        return redirect('/departments')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
