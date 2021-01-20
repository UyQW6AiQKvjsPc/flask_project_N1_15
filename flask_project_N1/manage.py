import views

from flask_migrate import MigrateCommand
from flask_script import Manager

from main import app
from blueprints import indexx, log_reg, moree, profile_b
from commands import CreateDataBase


# Register blueprints
app.register_blueprint(indexx, url_prefix='/in/')
app.register_blueprint(log_reg, url_prefix='/welcome/')
app.register_blueprint(moree, url_prefix='/more/')
app.register_blueprint(profile_b, url_prefix='/profile/')

manager = Manager(app)


if __name__ == "__main__":
    manager.add_command("createDataBase", CreateDataBase())
    manager.add_command('db', MigrateCommand)
    manager.run() # local
    # app.run()   # production