from . import db
from datetime import datetime


class UserShippingInfo(db.Model):
    __tablename__ = 'user_shipping_info'
    shipping_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    payment_id = db.Column(db.Integer, db.ForeignKey(
        'payments.payment_id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
