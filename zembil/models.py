from datetime import datetime
from zembil import db, bcrypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app as app


class UserModel(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String(300), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    phone = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    shops = db.relationship('ShopModel', back_populates='user')
    reviews = db.relationship('ReviewModel', back_populates='user')
    wishlists = db.relationship('WishListModel', back_populates='user')
    shops_followed = db.relationship(
        'ShopFollowerModel', back_populates='user')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_in=18000):
        s = Serializer(app.config['SECRET_KEY'], expires_in)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return UserModel.query.get(user_id)


class CategoryModel(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

    shops = db.relationship('ShopModel', back_populates='category')
    products = db.relationship('ProductModel', back_populates='category')


class LocationModel(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    __table_args__ = (db.UniqueConstraint('latitude', 'longitude'), )

    shop = db.relationship('ShopModel', back_populates='location')

class ShopModel(db.Model):
    __tablename__ = "shop"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    building_name = db.Column(db.String(300), nullable=False)
    phone_number1 = db.Column(db.String(50), nullable=True)
    phone_number2 = db.Column(db.String(50), nullable=True)
    image = db.Column(db.String(300), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Boolean, nullable=True)

    user = db.relationship('UserModel', back_populates='shops')
    location = db.relationship('LocationModel', back_populates='shop', cascade="all,delete")
    category = db.relationship('CategoryModel', back_populates='shops')
    products = db.relationship('ProductModel', back_populates='shop')
    ads = db.relationship('AdvertisementModel', backref='shop', lazy=True)
    followers = db.relationship('ShopFollowerModel', back_populates='shop')


class ShopFollowerModel(db.Model):
    __tablename__ = "shop_follower"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'shop_id'), )

    user = db.relationship('UserModel', back_populates='shops_followed')
    shop = db.relationship('ShopModel', back_populates='followers')

