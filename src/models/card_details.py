from . import db
from datetime import datetime


class CardDetails(db.Model):
    __tablename__ = 'card_details'
    # Primary Key
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Foreign Key linking to the user
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.user_id'), nullable=False)
    # Card Details
    # Ensure secure handling
    card_number = db.Column(db.String(20), nullable=False)
    card_holder_name = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(
        db.String(7), nullable=False)  # Format: MM/YYYY
    # Ensure secure handling of CVV
    cvv = db.Column(db.String(4), nullable=False)
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CardDetails(card_id={self.card_id}, user_id={self.user_id})>'
    # Helper Method to Mask Card Number

    def masked_card_number(self):
        """Return the card number with only the last 4 digits visible."""
        if len(self.card_number) > 4:
            return f"**** **** **** {self.card_number[-4:]}"
        return self.card_number
    # Validation Method for Expiration Date

    def is_card_expired(self):
        """Check if the card is expired based on the expiration date."""
        try:
            exp_month, exp_year = map(int, self.expiration_date.split('/'))
            exp_date = datetime(year=exp_year, month=exp_month, day=1)
            return exp_date < datetime.utcnow()
        except ValueError:
            raise ValueError(
                "Invalid expiration date format. Expected MM/YYYY.")
