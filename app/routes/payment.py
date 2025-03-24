from flask import Blueprint, render_template
from app.models.payment import Payment

payment = Blueprint('payment', __name__)

@payment.route('/payments')
def payments():
    # Logic to display all payments(pending/complete)
    payments = Payment.query.filter_by(user_id=current_user.id).all()
    return render_template('payment.html', payments=payments)