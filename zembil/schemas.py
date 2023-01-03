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


class LocationSchema(ma.Schema):
    class Meta:
        fields = ("id", "longitude", "latitude", "description")
        model = LocationModel
        ordered = True
    longitude = fields.Float(
        required=True, validate=lambda n: n > -180 and n < 180)
    latitude = fields.Float(
        required=True, validate=lambda n: n > -90 and n < 90)
    description = fields.String(
        required=True, validate=validate.Length(5), data_key="locationName")


class CategorySchema(ma.Schema):
    class Meta:
        fields = ("id", "name")
        model = CategoryModel
        ordered = True
    name = fields.String(required=True, data_key="categoryName")

class ShopSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "user_id", "location", "location_id", "category_id", "building_name", "phone_number1",
                  "phone_number2", "category", "image", "description", "status", "followers")
        model = ShopModel
        ordered = True
    name = fields.String(required=False, data_key="shopName")
    user_id = fields.Integer(data_key="userId")
    category_id = fields.Integer(required=True, data_key="categoryId")
    location_id = fields.Integer(data_key="shopLocationId")
    image = fields.String(required=False, data_key="imageUrl")
    category = fields.Pluck(CategorySchema, "name", dump_only=True)
    building_name = fields.String(required=False, data_key="buildingName")
    phone_number1 = fields.String(required=False, data_key="phoneNumber")
    phone_number2 = fields.String(required=False, data_key="phoneNumber2")
    description = fields.String(required=True)
    status = fields.Boolean(dump_only=True, data_key="isActive")

    location = ma.Nested(LocationSchema)
    followers = ma.Nested(UserSchema, only=['id'], many=True)

    @validates("phone_number1")
    @validates("phone_number2")
    def validate_mobile(self, value):
        rule = re.compile(r'^\+(?:[0-9]●?){6,14}[0-9]$')

        if not rule.search(value):
            msg = u"Invalid mobile number."
            raise ValidationError(msg)
