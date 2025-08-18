# backend/payments.py
import razorpay
from flask import Blueprint, request, jsonify
from datetime import datetime
from backend.utils import (
    DUES_CSV, TRANSACTIONS_CSV,
    read_csv, write_csv, ensure_headers, log_action
)

payments_bp = Blueprint("payments", __name__)

@payments_bp.route("/create_order", methods=["POST"])
def create_order():
    """
    Create a Razorpay order using keys provided (not stored).
    Body: { amount, mode, key_id, key_secret, upi_id, customer_name, username }
    """
    data = request.json or {}
    try:
        amount = int(data.get("amount", 0))
    except Exception:
        amount = 0
    mode = (data.get("mode") or "").lower()
    key_id = data.get("key_id")
    key_secret = data.get("key_secret")
    owner_upi = data.get("upi_id")
    customer_name = data.get("customer_name")
    username = data.get("username")

    if not all([amount > 0, mode in ("test", "live"), key_id, key_secret, owner_upi, customer_name, username]):
        return jsonify({"error": "Missing or invalid fields"}), 400

    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        order = client.order.create({
            "amount": amount * 100,  # paise
            "currency": "INR",
            "payment_capture": 1,
            "notes": {
                "mode": mode,
                "owner_upi": owner_upi,
                "customer": customer_name,
                "username": username
            }
        })
        return jsonify({
            "order_id": order["id"],
            "status": "created",
            "amount": amount
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payments_bp.route("/confirm_payment", methods=["POST"])
def confirm_payment():
    """
    Simulated confirmation endpoint for testing (replace with webhook in production).
    Body: { order_id, amount, customer_name, username, mode }
    """
    data = request.json or {}
    order_id = data.get("order_id")
    customer_name = data.get("customer_name")
    username = data.get("username")
    mode = (data.get("mode") or "test").lower()
    try:
        amount = float(data.get("amount", 0))
    except Exception:
        amount = 0.0

    if not all([order_id, customer_name, username, amount > 0]):
        return jsonify({"error": "Missing fields"}), 400

    # Reduce dues
    dues = read_csv(DUES_CSV)
    for d in dues:
        if d["username"] == username:
            current = float(d.get("due", 0))
            d["due"] = f"{max(0.0, current - amount):.2f}"
            break
    write_csv(DUES_CSV, ["username", "customer", "due"], dues)

    # Record transaction
    ensure_headers(TRANSACTIONS_CSV)
    with open(TRANSACTIONS_CSV, "a", newline="", encoding="utf-8") as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=["date", "username", "customer", "amount", "order_id", "status", "mode"])
        writer.writerow({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "customer": customer_name,
            "amount": f"{amount:.2f}",
            "order_id": order_id,
            "status": "Success",
            "mode": mode
        })

    log_action("payment_success", f"{username} paid {amount} (order {order_id})")
    return jsonify({"success": True, "message": "Payment confirmed, dues updated"}), 200
