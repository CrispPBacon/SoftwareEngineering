from flask_mail import Mail, Message

mail = Mail()


def load_mail_config(app):
    # MAIL CONFIG
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True  # Use TLS for encryption
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'swankymr@gmail.com'  # Your Gmail address
    app.config['MAIL_PASSWORD'] = 'rvawssbpvkaftvmi'     # Your App Password

    mail.init_app(app)
