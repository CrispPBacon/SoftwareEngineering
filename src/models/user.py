from . import db
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'LGBT+'), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone_number = db.Column(db.String(15), nullable=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

    @validates('email')
    def validate_email(self, key, email):
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        return email.lower()  # Normalize email to lowercase

    @validates('phone_number')
    def validate_phone_number(self, key, phone_number):
        if phone_number and not phone_number.isdigit():
            raise ValueError("Phone number must contain only digits")
        return phone_number

    @validates('role')
    def validate_role(self, key, role):
        allowed_roles = ['user', 'admin']
        if role not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}")
        return role

    def set_password(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', role='{self.role}')>"
