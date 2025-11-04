from flask_mail import Message
import uuid
from datetime import datetime, timedelta

from ..config import mail, SECRET_KEY
from ..models import User, db

from flask import current_app


def generate_token(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return None

    token = str(uuid.uuid4())  # random unique string
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(minutes=30)
    db.session.commit()
    return token


def send_reset_email(to_email, token):
    link = f"{current_app.config.get('FRONTEND_URL')}/reset-password/{token}"
    msg = Message("Password Reset Request",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[to_email])
    msg.body = f"Click the link to reset your password: {link}"
    mail.send(msg)
