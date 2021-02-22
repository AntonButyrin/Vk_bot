from pony.orm import Database, Required, Json

from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Создает состояние пользователя внутри сценария"""
    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)
    do_continue = True


class Registration(db.Entity):
    """Данные для бронирования"""
    user_id = Required(str)
    fro = Required(str)
    to = Required(str)
    data = Required(str)
    place = Required(str)
    result = Required(str)
    comment = Required(str)
    phone = Required(str)


db.generate_mapping(create_tables=True)
