from . import db
from datetime import datetime


class Payment(db.Model):
    __tablename__ = 'payments'
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'orders.order_id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(
        db.Enum('Cash on Delivery', 'E-Wallet', 'Card'), nullable=False)
    e_wallet_provider = db.Column(db.Enum('GCASH', 'MAYA'), nullable=True)
    card_provider = db.Column(
        db.Enum('BDO', 'BPI', 'MetroBank'), nullable=True)
    transaction_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
