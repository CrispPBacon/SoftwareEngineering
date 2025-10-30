from . import db
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    sale_id = db.Column(db.Integer, db.ForeignKey(
        'sales.sale_id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Establish relationship with Sale
    sale = db.relationship('Sale', backref='orders', lazy=True)

    def __repr__(self):
        return (f"<Order(order_id={self.order_id}, user_id={self.user_id}, "
                f"sale_id={self.sale_id}, product_name='{self.product_name}', "
                f"price={self.price}, category='{self.category}', "
                f"created_at={self.created_at})>")
