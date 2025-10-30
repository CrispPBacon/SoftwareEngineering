from . import db


class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String(255), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
