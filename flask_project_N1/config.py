class Config(object):
    # Debug mode
    DEBUG = True

    # Hosting info
    DOMAIN = "ada.atrecon.ru"

    # Create dummy secret key to use sessions
    SECRET_KEY = 'dsfgklwer32450345jfs}{DLI*(#)#@*&#*&$@mgdflgkfewro32054348terksdfjskfsndmclsfdi920529&&&*jjfsADSD'

    # Set optional bootswatch theme
    FLASK_ADMIN_SWATCH = 'cerulean'

    # Create in-memory database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SNMP
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'cookie96112@gmail.com' # поменять на почтовый ящик сайта
    MAIL_DEFAULT_SENDER = 'cookie96112@gmail.com'  # поменять на почтовый ящик сайта
    MAIL_PASSWORD = 'Kb1749566000'  # пароль


# Конфиг для разработки
class DevelopConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flask_project.db'


# Конфиг для тестов
class TestConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


# Конфиг для продакшена
class ProductionConfig(Config):
    DEBUG = False
