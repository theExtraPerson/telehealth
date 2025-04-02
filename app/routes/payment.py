import uuid

from flask import Blueprint, request, jsonify

from app.models.payments import Payment

payment = Blueprint("payment", __name__, template_folder="../../templates/payment")


@payment.route("/make_payment", methods=["POST"])
def make_payment():
    """Handle payment processing"""
    data = request.get_json()

    user_id = data.get("user_id")
    appointment_id = data.get("appointment_id")
    amount = data.get("amount")
    payment_method = data.get("payment_method")

    if not user_id or not amount or not payment_method:
        return jsonify({"error": "Missing required fields"}), 400

    transaction_id = str(uuid.uuid4())  # Generate unique transaction ID

    new_payment = Payment(
        user_id=user_id,
        appointment_id=appointment_id,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        status="pending"
    )
    new_payment.save_to_db()

    return jsonify({
        "message": "Payment initiated successfully",
        "transaction_id": transaction_id,
        "status": new_payment.status
    }), 201


@payment.route("/payment_status/<string:transaction_id>", methods=["GET"])
def check_payment_status(transaction_id):
    """Check the status of a payment"""
    payments = Payment.find_by_transaction_id(transaction_id)
    if payments:
        return jsonify({
            "transaction_id": payments.transaction_id,
            "status": payments.status,
            "amount": payments.amount,
            "payment_method": payments.payment_method
        }), 200
    return jsonify({"error": "Transaction not found"}), 404


