from flask_script import Command
from main import db
from models import Users, TemporaryData


class CreateDataBase(Command):
    'Создаем базу данных и объявляем все таблицы'
    db.create_all()



