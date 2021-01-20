# https://ploshadka.net/flask-delaem-avtorizaciju-na-sajjte/
from datetime import datetime
from flask_login import UserMixin
# from flask_security import RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash

from main import app, db


# roles_users = db.Table(
#     'roles_users',
#     db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
# )


# class Role(db.Model, RoleMixin):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))

#     def __str__(self):
#         return self.name


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # Уникальный id пользователя
    user_id = db.Column(db.TEXT, nullable=True, unique=True)
    # Логин и пока что username
    login = db.Column(db.String(60), unique=True, nullable=False, default=0)
    # Почта
    email = db.Column(db.String(100), unique=True, nullable=False, default=0)
    # Пароль
    psw = db.Column(db.TEXT, nullable=False, unique=True, default=0)
    # Мобильный номер
    phone = db.Column(db.String(15), unique=True, nullable=False, default=0)
    # Баланс пользователя
    balance = db.Column(db.TEXT, nullable=True, default=0)
    # Дата рождения
    birth = db.Column(db.TEXT, nullable=True)
    # Дата создания аккаунта
    data_create = db.Column(db.DateTime, default=datetime.utcnow)
    # Дата последнего обновления данных о пользователе
    data_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Пол
    gender = db.Column(db.TEXT, nullable=True)
    # Начало тарифа
    rate_start = db.Column(db.TEXT, nullable=True)
    # Конец тарифа
    rate_end = db.Column(db.TEXT, nullable=True)
    # Название тарифа
    rate_name = db.Column(db.TEXT, nullable=True)
    # Статус регистрации
    status_reg = db.Column(db.TEXT, nullable=False, default=0)
    # Временные данные пользователя
    temp_data = db.relationship('TemporaryData', backref='users', uselist=False)
    # ???
    # name = db.Column(db.String)
    # username = db.Column(db.String, unique=True)
    # email = db.Column(db.String, unique=True)
    # password = db.Column(db.String)
    # created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    # updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    # Нужен для security!
    # active = db.Column(db.Boolean())
    # Для получения доступа к связанным объектам
    # roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class TemporaryData(db.Model):
    __tablename__ = 'temporary_data'
    id = db.Column(db.Integer, primary_key=True)
    # Список данных
    temp_items = db.Column(db.TEXT, nullable=True)
    # Статус "waiting" - ожидание подтверждения, "confirmed" - подтверждены
    status = db.Column(db.TEXT, nullable=True)
    # Привязка к пользователю
    user_id = db.Column(db.TEXT, db.ForeignKey('users.user_id'))


# Flask - Login
    # @property
    # def is_authenticated(self):
    #     return True

    # @property
    # def is_active(self):
    #     return True

    # @property
    # def is_anonymous(self):
    #     return False

    # Flask-Security
    # def has_role(self, *args):
    #     return set(args).issubset({role.name for role in self.roles})

    # def get_id(self):
    #     return self.id

    # Required for administrative interface
    # def __unicode__(self):
    #     return self.username

    # def set_password(self, password):
    #     self.password = generate_password_hash(password)

    # def check_password(self, password):
    #     return check_password_hash(self.password, password)


# Отвечает за сессию пользователей. Запрещает доступ к роутам, перед которыми указано @login_required
# @login_manager.user_loader
# def load_user(user_id):
#     return db.session.query(User).get(user_id)


class OzonCategory(db.Model):
    """ Ozon - Категория """
    __tablename__ = 'ozon_сategory'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(50), unique=True)
    ozon_product = db.relationship('OzonProduct', backref='ozon_cat', uselist=True)

    def __repr__(self):
        return f'<OzonCategory {self.title}>'


class OzonProduct(db.Model):
    """ Ozon - Продукт """
    __tablename__ = 'ozon_product'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=True)
    cat_id = db.Column(db.INT, db.ForeignKey('ozon_сategory.id'))
    title = db.Column(db.String(255), nullable=True)
    brand = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(50), unique=True)
    article = db.Column(db.String(255), nullable=True)
    product_link = db.Column(db.String(255), nullable=True)
    image_link = db.Column(db.String(255), nullable=True)
    product_info = db.relationship('OzonProductInfo', backref='ozon_product', uselist=False)

    def __repr__(self):
        return f'<OzonProduct {str(self.id) + " - " + self.title}>'

    def get_absolute_url(self):
        url = '/ozon/catalog/' + str(self.slug)
        return url


class OzonProductInfo(db.Model):
    """ Ozon - Информация о продуукте """
    __tablename__ = 'ozon_product_info'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=True)
    product = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.INT, db.ForeignKey('ozon_product.id'))
    date = db.Column(db.TEXT, nullable=True)
    price = db.Column(db.String(255), nullable=True)
    discount = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.String(255), nullable=True)
    count = db.Column(db.INT, nullable=True)
    comments_count = db.Column(db.INT, nullable=True)

    def __repr__(self):
        return self.product


class WildBerriesCategory(db.Model):
    """ WildBerries - Категория """
    __tablename__ = 'wildberries_category'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(50), unique=True)
    wild_sub = db.relationship('WildBerriesSubcategory', backref='wild_cat', uselist=True)
    wild_sub_sub = db.relationship('WildBerriesSubSubcategory', backref='wild_cat', uselist=True)
    wild_product = db.relationship('WildBerriesProduct', backref='wild_cat', uselist=True)

    def __repr__(self):
        return f'<WildBerriesCategory {self.title}>'


class WildBerriesSubcategory(db.Model):
    """ WildBerries - Подкатегория """
    __tablename__ = 'wildberries_subcategory'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=True)
    cat_id = db.Column(db.TEXT, db.ForeignKey('wildberries_category.id'))
    title = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f'<WildBerriesSubcategory {self.title}>'


class WildBerriesSubSubcategory(db.Model):
    """ WildBerries - Под-подкатегория """
    __tablename__ = 'wildberries_sub_subcategory'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=True)
    cat_id = db.Column(db.INT, db.ForeignKey('wildberries_category.id'))
    subcategory = db.Column(db.String(255), nullable=True)
    subcat_id = db.Column(db.INT, nullable=True)
    title = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<WildBerriesSubSubcategory {self.title}>'


class WildBerriesProduct(db.Model):
    """ WildBerries - Продукт """
    __tablename__ = 'wildberries_product'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=True) # Убрать
    cat_id = db.Column(db.INT, db.ForeignKey('wildberries_category.id'))
    subcategory = db.Column(db.String(255), nullable=True) # Убрать
    subcat_id = db.Column(db.INT, nullable=True)
    sub_subcategory = db.Column(db.String(255), nullable=True) # Убрать
    sub_subcategory_id = db.Column(db.INT, nullable=True)
    title = db.Column(db.String(255), nullable=True)
    slug = db.Column(db.String(50), unique=True)
    article = db.Column(db.String(255), nullable=True)
    product_link = db.Column(db.String(255), nullable=True)
    image_link = db.Column(db.String(255), nullable=True)
    wild_product_info = db.relationship('WildBerriesProductInfo', backref='wild_product', uselist=True)
    wild_size = db.relationship('WildBerriesSize', backref='wild_product', uselist=True)
    wild_info = db.relationship('WildBerriesCount', backref='wild_product', uselist=True)

    def __repr__(self):
        return f'<WildBerriesProduct {str(self.id) + " - " + self.title}>'

    def get_absolute_url(self):
        url = '/wildberries/catalog/' + str(self.slug)
        return url


class WildBerriesProductInfo(db.Model):
    """ WildBerries - Информация о продукте """
    __tablename__ = 'wildberries_product_info'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=True)
    subcategory = db.Column(db.String(255), nullable=True)
    sub_subcategory = db.Column(db.String(255), nullable=True)
    product = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.TEXT, db.ForeignKey('wildberries_product.id'))
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    price = db.Column(db.String(255), nullable=True)
    discount = db.Column(db.String(255), nullable=True)
    rating = db.Column(db.String(255), nullable=True)
    comments_count = db.Column(db.INT, nullable=True)

    def __repr__(self):
        return f'<WildBerriesProductInfo {str(self.product) + str(self.date)}>'


class WildBerriesStore(db.Model):
    """ WildBerries - Склад """
    __tablename__ = 'wildberries_store'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return self.title


class WildBerriesSize(db.Model):
    """ WildBerries - Размер """
    __tablename__ = 'wildberries_size'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.TEXT, db.ForeignKey('wildberries_product.id'))
    title = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<WildBerriesSize {str(self.product) + " - " + self.title}>'


class WildBerriesCount(db.Model):
    """ WildBerries - Кол-во на складе """
    __tablename__ = 'wildberries_count'
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.INT, db.ForeignKey('wildberries_product.id'))
    date = db.Column(db.TEXT, default=datetime.utcnow)
    size = db.Column(db.String(255), nullable=True)
    store_id = db.Column(db.INT, nullable=True)
    store_slug = db.Column(db.String(50), nullable=True)
    store_title = db.Column(db.String(255), nullable=True)
    count = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<WildBerriesCount {str(self.product) + str(self.size) + " - " + str(self.store_title) + " - " + str(self.date)}>'
