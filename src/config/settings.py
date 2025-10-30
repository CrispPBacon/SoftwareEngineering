from . import ENV, SECRET_KEY, PORT, SQLALCHEMY_DATABASE_URI, FRONTEND_URL
from ..models import db
from sqlalchemy.exc import OperationalError


def load_config(app):
    # GENERAL CONFIG
    app.config["ENV"] = ENV
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["PORT"] = PORT
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FRONTEND_URL'] = FRONTEND_URL

    # Initialize database
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
        except OperationalError as e:
            print(f"Error creating tables: {e}")
