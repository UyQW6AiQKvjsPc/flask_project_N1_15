import os.path

from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_mail import Mail

from config import DevelopConfig

app = Flask(__name__)
app.config.from_object(DevelopConfig)

# Create directory for file fields to use
file_path = os.path.join(os.path.dirname(__file__), 'static/files')


admin = Admin(app, name='Admin panel', template_mode='bootstrap3')
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
mail = Mail(app)
migrate = Migrate(app,  db)
# login_manager = LoginManager(app)



