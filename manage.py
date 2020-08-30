import os

from dotenv import load_dotenv
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app, api
import db
from app.controllers.user import UsersAuthController, UsersRegisterController, UsersController

database = db.get_db()

load_dotenv()

app = create_app(os.environ['APP_SETTINGS'])
migrate = Migrate(app, database)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

api.add_resource(UsersAuthController, '/users/auth')
api.add_resource(UsersRegisterController, '/users/register')
api.add_resource(UsersController, '/users/<int:id>')

if __name__ == '__main__':
    manager.run()
