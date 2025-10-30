from flask import Flask
from .routes import main_bp, user_bp, admin_bp
from .config import load_config, load_mail_config
from .utils import register_error_handlers, inject_role


def create_app():
    # Initialization
    app = Flask(__name__, template_folder="../templates")
    load_config(app)
    load_mail_config(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    # Register context processors
    app.context_processor(inject_role)

    # Register error handlers
    register_error_handlers(app)
    return app
