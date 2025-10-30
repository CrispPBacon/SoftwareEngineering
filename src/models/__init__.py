from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Import models after db definition
# fmt: off  # disable formatting temporarily (Black)
from .card_details import CardDetails
from .cart_item import CartItem
from .order import Order
from .payment import Payment
from .product import Product
from .sale import Sale
from .showcase_image import ShowcaseImage
from .user_shipping_info import UserShippingInfo
from .user import User
