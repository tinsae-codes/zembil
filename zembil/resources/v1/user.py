from datetime import timedelta
from markupsafe import escape
from flask import current_app, request, jsonify, make_response
from flask_restful import Resource, abort, reqparse
from flask_jwt_extended import (create_access_token, get_jwt,
                                jwt_required, get_jwt_identity)
from marshmallow import ValidationError
from zembil import db, mail
from zembil.models import UserModel, RevokedTokenModel, ShopModel, AdvertisementModel, ProductModel
from zembil.schemas import UserSchema
from zembil.common.util import clean_null_terms

from flask_mail import Message

user_schema = UserSchema()
users_schema = UserSchema(many=True)

user_auth_arguments = reqparse.RequestParser()
user_auth_arguments.add_argument(
    'username', type=str, help="Username", required=True)
user_auth_arguments.add_argument(
    'password', type=str, help="Password", required=True)

auth_reset_arguments = reqparse.RequestParser()
auth_reset_arguments.add_argument(
    'email', type=str, help="Enter your associated email", required=True)
auth_reset_arguments.add_argument(
    'host', type=str, help="Provide the client host address", required=True)

new_passwd_arguments = reqparse.RequestParser()
new_passwd_arguments.add_argument(
    'new_password', type=str, help='Enter new password', required=True)


class Users(Resource):
    @jwt_required()
    def get(self):
        role = get_jwt()['role']
        if role == 'user':
            user_id = get_jwt_identity()
            result = UserModel.query.filter_by(id=user_id).first()
            return user_schema.dump(result)
        users = UserModel.query.all()
        return users_schema.dump(users)

    def post(self):
        data = request.get_json()
        try:
            args = user_schema.load(data)
        except ValidationError as errors:
            abort(400, message=errors.messages)
        user = UserModel(
            **args,
            # role="admin"
        )
        db.session.add(user)
        db.session.commit()
        return user_schema.dump(user), 201


class User(Resource):
    @jwt_required()
    def get(self, id):
        result = UserModel.query.filter_by(id=id).first()
        if not result:
            abort(404, message="User not found!")
        return user_schema.dump(result)

    @jwt_required()
    def patch(self, id):
        data = request.get_json()
        try:
            args = UserSchema(partial=True).load(data)
        except ValidationError as errors:
            abort(400, message=errors.messages)
        args = clean_null_terms(args)
        user_id = get_jwt_identity()
        if user_id == id:
            existing = UserModel.query.filter_by(id=id).update(args)
        return abort(403, message="User not authorized!")

