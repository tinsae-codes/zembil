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

