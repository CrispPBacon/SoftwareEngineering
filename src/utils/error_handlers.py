from flask import render_template, redirect, url_for


def register_error_handlers(app):
    """Register custom error handlers with the Flask app."""

    @app.errorhandler(500)
    def internal_server_error(error):
        print(f"Internal Server Error: {error}")
        return redirect(url_for('main.menu'))

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
