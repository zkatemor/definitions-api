import hashlib
import uuid

from flask_restful import Resource, reqparse
from models.user import User, db


class UsersAuthController(Resource):
    def auth_schema(self, user):
        return {'id': user.id, 'login': user.login, 'token': user.token}

    def error_schema(self):
        return {
            "error":
                {
                    "message": "Неверный логин или пароль."
                }
        }

    def encrypt_string(self, hash_string):
        sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
        return sha_signature

    def auth_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        return args['login'], args['password']

    def post(self):
        login, password = self.auth_params()
        password_sha = self.encrypt_string(password)

        user = User.query.filter(User.login == login
                                 and User.password == password_sha).first()

        if user:
            user_json = self.auth_schema(user)
            return user_json, 200
        else:
            return self.error_schema(), 404


class UsersRegisterController(Resource):
    def register_schema(self, user):
        return {'id': user.id, 'login': user.login, 'token': user.token}

    def encrypt_string(self, hash_string):
        sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
        return sha_signature

    def register_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('token', type=str, required=True)
        args = parser.parse_args()
        return args['login'], args['password'], args['token']

    def post(self):
        login, password, token = self.register_params()
        password_sha = self.encrypt_string(password)

        superuser = User.query.filter(User.token == token).first()

        if superuser:
            if superuser.login == 'megamind':
                if superuser.password == self.encrypt_string('111'):
                    token = uuid.uuid4()
                    user = User(login, password_sha, token)
                    db.session.add(user)
                    db.session.commit()
                    return self.register_schema(user), 200
        else:
            return {
                       "error": {
                               "message": "У вас нет прав на создание пользователя."
                           }
                   }, 401