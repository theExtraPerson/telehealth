from datetime import datetime
from app import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # Pending, Completed, Failed
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., Credit Card, PayPal, Mobile Money
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='payments', lazy=True)
    appointment = db.relationship('Appointment', backref='payment', lazy=True)

    def __repr__(self):
        return f"<Payment {self.transaction_id} - {self.amount} - {self.status}>"

    def save_to_db(self):
        """Save the payment instance to the database."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_transaction_id(cls, transaction_id):
        """Retrieve payment details by transaction ID."""
        return cls.query.filter_by(transaction_id=transaction_id).first()

    @classmethod
    def get_payments_by_user(cls, user_id):
        """Retrieve all payments made by a user."""
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def update_status(cls, transaction_id, new_status):
        """Update payment status."""
        payment = cls.find_by_transaction_id(transaction_id)
        if payment:
            payment.status = new_status
            db.session.commit()
            return True
        return False
