from flask_mail import Mail, Message
from . import MAIL_PASSWORD, MAIL_SERVER, MAIL_USERNAME
mail = Mail()


def load_mail_config(app):
    # MAIL CONFIG
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True  # Use TLS for encryption
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = MAIL_USERNAME  # Your Gmail address
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD     # Your App Password

    mail.init_app(app)
