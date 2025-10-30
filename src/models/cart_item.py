from . import db


class CartItem(db.Model):
    __tablename__ = 'cart_items'
    cart_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'products.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
