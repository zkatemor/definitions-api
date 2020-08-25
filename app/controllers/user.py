import hashlib
import uuid

from flask_restful import Resource, reqparse
from models.user import User, db


class UsersAuthController(Resource):
    def auth_schema(self, user):
        json = {'id': user.id, 'login': user.login, 'token': user.token}
        return json

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
        # TODO: переписать пушо ТЗ говно было
        login, password = self.auth_params()
        password_sha = self.encrypt_string(password)
        token = uuid.uuid1()

        user = User(login, password_sha, token)
        db.session.add(user)
        db.session.commit()

        user_json = self.auth_schema(user)
        return user_json
