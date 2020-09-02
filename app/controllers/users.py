import hashlib
import os
import uuid

from flask_restful import Resource, reqparse
from models.user import User, db


def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


def body_schema(user):
    return {"result": {'id': user.id, 'login': user.login, 'token': user.token}}


def schema(users):
    return {"result": [{'id': user.id, 'login': user.login, 'token': user.token} for user in users]}


class UsersAuthController(Resource):
    def error_schema(self):
        return {
            "error":
                {
                    "message": "wrong login or password"
                }
        }

    def auth_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        return args['login'], args['password']

    def post(self):
        """
        file: docs/users/auth.yml
        """
        try:
            login, password = self.auth_params()
            password_sha = encrypt_string(password)
        except Exception as e:
            return {
                       "error": {
                           "message": "login, password is required"
                       }
                   }, 422

        user = User.query.filter(User.login == login).first()
        if user and user.password == password_sha:
            return body_schema(user), 200
        else:
            return self.error_schema(), 404


class UsersRegisterController(Resource):
    def register_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('token', type=str, required=True)
        args = parser.parse_args()
        return args['login'], args['password'], args['token']

    def post(self):
        """
        file: docs/users/register.yml
        """
        try:
            login, password, token = self.register_params()
            password_sha = encrypt_string(password)
        except Exception as e:
            return {
                       "error": {
                           "message": "login, password, token is required"
                       }
                   }, 422

        superuser = User.query.filter(User.token == token).first()

        if superuser and superuser.login == os.environ['ADMIN'] and superuser.password == encrypt_string(
                os.environ['PASSWORD']):
            token = uuid.uuid4()
            try:
                user = User(login, password_sha, token)
                db.session.add(user)
                db.session.commit()
                return body_schema(user), 200
            except Exception as e:
                return {
                           "error": {
                               "message": "login already exists"
                           }
                       }, 418

        else:
            return {
                       "error": {
                           "message": "you don't have enough rights"
                       }
                   }, 401


class UsersListController(Resource):
    def get(self):
        """
        file: docs/users/index.yml
        """
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, required=True)
            args = parser.parse_args()
            token = args['token']
        except Exception as e:
            return {
                       "error": {
                           "message": "token is required"
                       }
                   }, 422

        user = User.query.filter(User.token == token).first()

        if user:
            query = User.query.order_by(User.id).all()
            data = schema(query)
            return data, 200
        else:
            return {
                       "error": {
                           "message": "you don't have enough rights"
                       }
                   }, 401


class UsersController(Resource):
    def update_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=False)
        parser.add_argument('password', type=str, required=False)
        parser.add_argument('token', type=str, required=True)
        args = parser.parse_args()
        return args['login'], args['password'], args['token']

    def put(self, id):
        """
        file: docs/users/update.yml
        """
        try:
            login, password, token = self.update_params()
        except Exception as e:
            return {
                       "error": {
                           "message": "token is required"
                       }
                   }, 422

        superuser = User.query.filter(User.token == token).first()

        if superuser and superuser.login == os.environ['ADMIN'] \
                and superuser.password == encrypt_string(os.environ['PASSWORD']):
            try:
                user = User.query.filter(User.id == id).first()
                if user is not None:
                    try:
                        if login:
                            User.query.filter_by(id=id).update({'login': login})

                        if password:
                            password_sha = encrypt_string(password)
                            User.query.filter_by(id=id).update({'password_sha': password_sha})

                        db.session.commit()
                        user = User.query.filter(User.id == id).first()
                        return body_schema(user), 200
                    except Exception as e:
                        return {
                                   "error": {
                                       "message": "login already exists"
                                   }
                               }, 400
                else:
                    return {
                               "error": {
                                   "message": "user not found"
                               }
                           }, 422

            except Exception as e:
                return {
                           "error": {
                               "message": str(e)
                           }
                       }, 400
        else:
            return {
                       "error": {
                           "message": "you don't have enough rights"
                       }
                   }, 401

    def delete(self, id):
        """
        file: docs/users/delete.yml
        """
        try:
            login, password, token = self.update_params()
        except Exception as e:
            return {
                       "error": {
                           "message": "token is required"
                       }
                   }, 422

        superuser = User.query.filter(User.token == token).first()

        if superuser and superuser.login == os.environ['ADMIN'] \
                and superuser.password == encrypt_string(os.environ['PASSWORD']):
            try:
                user = User.query.filter(User.id == id).first()
                if user is not None:
                    User.query.filter(User.id == id).delete()
                    db.session.commit()
                    return {"success": True}, 200
                else:
                    return {
                               "error": {
                                   "message": "user not found"
                               }
                           }, 404

            except Exception as e:
                return {
                           "error": {
                               "message": str(e)
                           }
                       }, 400
        else:
            return {
                       "error": {
                           "message": "you don't have enough rights"
                       }
                   }, 401
