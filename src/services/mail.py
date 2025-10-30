from flask_mail import Message
from ..config import mail, SECRET_KEY
from itsdangerous import URLSafeTimedSerializer

from flask import current_app


def send_token_to_email(recipient, token):
    msg = Message(
        subject='Crisppbacon Page Forget Password',
        sender='swankymr@gmail.com',  # Ensure this matches MAIL_USERNAME
        recipients=[f'{recipient}']  # Replace with actual recipient's email
    )
    msg.body = f"Forget password click here to reset your password: https://crisppbacon.pythonanywhere.com/reset/{token}"
    mail.send(msg)


def generate_token(email):
    s = URLSafeTimedSerializer(SECRET_KEY)
    return s.dumps(email, salt='password-reset-salt')


def confirm_token(token, expiration=3600):
    s = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expiration)
    except:
        return False
    return email


def send_reset_email(to_email, token):
    link = f"{current_app.config.get('FRONTEND_URL')}/reset-password/{token}"
    msg = Message("Password Reset Request",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[to_email])
    msg.body = f"Click the link to reset your password: {link}"
    mail.send(msg)
