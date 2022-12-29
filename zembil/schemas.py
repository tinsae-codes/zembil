import re
from marshmallow import fields, validate, validates, ValidationError
from zembil import ma
from zembil.models import *


class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "username", "password", "email", "date", "role", "phone")
        model = UserModel
        ordered = True
    id = fields.Integer(dump_only=True, data_key="userId")
    name = fields.String(required=False)
    username = fields.String(required=True)
    password = fields.String(
        required=True, load_only=True, data_key="password")
    email = fields.Email(required=True)
    role = fields.String()
    phone = fields.String(required=False)
    date = fields.DateTime(dump_only=True, data_key="dateAccountCreated")

    @validates("phone")
    def validate_mobile(self, value):
        rule = re.compile(r'^\+(?:[0-9]●?){6,14}[0-9]$')

        if not rule.search(value):
            msg = u"Invalid mobile number."
            raise ValidationError(msg)

    @validates("username")
    def validate_username(self, username):
        if bool(UserModel.query.filter_by(username=username).first()):
            raise ValidationError(
                'username already exists, please use a different username.'
            )

    @validates("email")
    def validate_email(self, email):
        if bool(UserModel.query.filter_by(email=email).first()):
            raise ValidationError(
                'email already exists, please use a different email.'
            )

