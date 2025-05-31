from datetime import datetime
from sqlalchemy import text, Numeric
from app import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    
    # Monetary values should use Numeric for precise calculations
    total_amount = db.Column(Numeric(10, 2), nullable=False)  # Changed from Float
    tax_amount = db.Column(Numeric(10, 2), server_default=text('0.00'))  # Added
    discount_amount = db.Column(Numeric(10, 2), server_default=text('0.00'))  # Added
    net_amount = db.Column(Numeric(10, 2), nullable=False)  # Added
    
    status = db.Column(db.String(20), nullable=False, 
                      server_default=text("'pending'"))  # Pending, Completed, Failed, Refunded
    payment_method = db.Column(db.String(50), nullable=False)  # Credit Card, PayPal, Mobile Money
    payment_gateway = db.Column(db.String(50))  # Added - Stripe, PayPal, Flutterwave etc.
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    gateway_reference = db.Column(db.String(100))  # Added - Gateway's transaction ID
    
    # Payment metadata
    currency = db.Column(db.String(3), server_default=text("'Ugx'"))  # Added
    is_recurring = db.Column(db.Boolean, server_default=text('0'))  # Added
    receipt_url = db.Column(db.String(255))  # Added - Link to payment receipt
    
    # Timestamps with SQL Server defaults
    created_at = db.Column(db.DateTime, nullable=False, 
                          server_default=text('GETDATE()'))
    updated_at = db.Column(db.DateTime, nullable=False, 
                          server_default=text('GETDATE()'), 
                          onupdate=text('GETDATE()'))
    completed_at = db.Column(db.DateTime)  # Added
    
    # Relationships
    user = db.relationship('User', backref='payments')
   
    def __repr__(self):
        return f"<Payment {self.id} - {self.transaction_id} - {self.net_amount} {self.currency}>"

    def __init__(self, **kwargs):
        super(Payment, self).__init__(**kwargs)
        # Calculate net amount if not provided
        if self.net_amount is None:
            self.net_amount = self.total_amount - self.discount_amount + self.tax_amount

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
        return cls.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()

    @classmethod
    def update_status(cls, transaction_id, new_status):
        """Update payment status."""
        payment = cls.find_by_transaction_id(transaction_id)
        if payment:
            payment.status = new_status
            if new_status.lower() == 'completed':
                payment.completed_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @property
    def is_successful(self):
        return self.status.lower() == 'completed'

    @property
    def formatted_amount(self):
        return f"{self.currency} {self.net_amount:.2f}"

    __table_args__ = (
        db.Index('ix_payments_user', 'user_id'),
        db.Index('ix_payments_status', 'status'),
        db.Index('ix_payments_created', 'created_at'),
        db.CheckConstraint('net_amount = total_amount - discount_amount + tax_amount', 
                         name='ck_payment_amounts'),
    )