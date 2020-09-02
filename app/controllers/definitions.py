import os

from flask_restful import Resource, reqparse, abort
from sqlalchemy import or_

from app.controllers.users import encrypt_string
from models.definition import Definition, db
from models.user import User


def body_schema(definition):
    return {"result": {'id': definition.id,
                       'title': definition.title,
                       'definition': definition.definition,
                       'link': definition.link}}


def schema(definition):
    return {'id': definition.id,
            'title': definition.title,
            'definition': definition.definition,
            'link': definition.link}


class DefinitionsListController(Resource):
    def paginated_list(self, results, page, count):
        page = int(page)
        count = int(count)
        total_count = len(results)

        obj = {'offset': page, 'limit': count, 'total_count': total_count}

        result = {'results': results[(page - 1):(page - 1 + count)], 'metadata': obj}
        return result

    def index_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('search', type=str, required=False)
        parser.add_argument('offset', type=int, required=True)
        parser.add_argument('limit', type=int, required=True)
        args = parser.parse_args()
        return args['search'], args['offset'], args['limit']

    def create_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('definition', type=str, required=True)
        parser.add_argument('link', type=str, required=True)
        parser.add_argument('token', type=str, required=True)
        args = parser.parse_args()
        return args['title'], args['definition'], args['link'], args['token']

    def get(self):
        search, page, count = self.index_params()
        query = Definition.query.order_by(Definition.id).all()
        if search:
            q = f"%{search}%"
            query = Definition.query.filter(or_(
                Definition.title.ilike(q),
                Definition.definition.ilike(q),
                Definition.link.ilike(q)
            ))

        data = [schema(definition) for definition in query]

        if 0 < len(data) < page or count < 0:
            return {
                       "error": {
                           "message": "page or count not found"
                       }
                   }, 404

        return self.paginated_list(data, page=page, count=count), 200

    def post(self):
        try:
            title, definition, link, token = self.create_params()
        except Exception as e:
            return {
                       "error": {
                           "message": "title, definition, link, token is required"
                       }
                   }, 422

        superuser = User.query.filter(User.token == token).first()

        if superuser and superuser.login == os.environ['ADMIN'] and superuser.password == encrypt_string(
                os.environ['PASSWORD']):
            try:
                definition = Definition(title, definition, link)
                db.session.add(definition)
                db.session.commit()
                return body_schema(definition), 200
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


class DefinitionsController(Resource):
    def update_params(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=False)
        parser.add_argument('definition', type=str, required=False)
        parser.add_argument('link', type=str, required=False)
        parser.add_argument('token', type=str, required=True)
        args = parser.parse_args()
        return args['title'], args['definition'], args['link'], args['token']

    def get(self, id):
        try:
            definition = Definition.query.filter_by(id=id).first()
            return body_schema(definition), 200
        except Exception as e:
            return {
                       "error": {
                           "message": 'definition not found'
                       }
                   }, 404

    def put(self, id):
        try:
            title, definition_text, link, token = self.update_params()
        except Exception as e:
            return {
                       "error": {
                           "message": "token is required"
                       }
                   }, 422

        superuser = User.query.filter(User.token == token).first()

        if superuser and superuser.login == os.environ['ADMIN'] and superuser.password == encrypt_string(
                os.environ['PASSWORD']):
            try:
                definition = Definition.query.filter(Definition.id == id).first()
                if definition is not None:
                    try:
                        if title:
                            Definition.query.filter_by(id=id).update({'title': title})

                        if definition_text:
                            Definition.query.filter_by(id=id).update({'definition': definition_text})

                        if link:
                            Definition.query.filter_by(id=id).update({'link': link})

                        db.session.commit()
                        definition = Definition.query.filter(Definition.id == id).first()
                        return body_schema(definition), 200
                    except Exception as e:
                        return {
                                   "error": {
                                       "message": str(e)
                                   }
                               }, 400
                else:
                    return {
                               "error": {
                                   "message": "definition not found"
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
        try:
            title, definition_text, link, token = self.update_params()
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
                definition = Definition.query.filter(Definition.id == id).first()
                if definition is not None:
                    Definition.query.filter(Definition.id == id).delete()
                    db.session.commit()
                    return {"success": True}, 200
                else:
                    return {
                               "error": {
                                   "message": "definition not found"
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
