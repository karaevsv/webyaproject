from data import db_session
from data.users import User


def main():
    db_session.global_init("db/base.sqlite")
    user = User()
    user.login = 'adm'
    user.set_password("12345")
    user.is_admin = True

    user1 = User()
    user1.login = 'oth'
    user1.set_password("12345")
    user1.is_admin = False

    session = db_session.create_session()
    session.add(user)
    session.add(user1)
    session.commit()


if __name__ == '__main__':
    main()