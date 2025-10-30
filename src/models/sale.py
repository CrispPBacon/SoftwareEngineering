from . import db
from datetime import datetime


class Sale(db.Model):
    __tablename__ = 'sales'
    sale_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.product_id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
