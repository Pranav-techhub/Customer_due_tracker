from flask import Blueprint, request, jsonify
from backend.services import (
    create_customer_account,
    change_password_service,
    record_offline_payment
)

routes_bp = Blueprint("routes", __name__)

@routes_bp.route("/create_customer", methods=["POST"])
def create_customer():
    data = request.json or {}
    try:
        username, password = create_customer_account(
            name=data.get("name", "").strip(),
            email=(data.get("email") or "").strip(),
            phone=(data.get("phone") or "").strip()
        )
        return jsonify({"username": username, "password": password}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@routes_bp.route("/change_password", methods=["POST"])
def change_password():
    data = request.json or {}
    username = data.get("username", "").strip()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    if not (username and old_password and new_password):
        return jsonify({"error": "Missing fields"}), 400
    res = change_password_service(username, old_password, new_password)
    code = 200 if "success" in res else 401
    return jsonify(res), code

@routes_bp.route("/record_offline_payment", methods=["POST"])
def record_offline_payment_api():
    data = request.json or {}
    username = data.get("username", "").strip()
    customer = data.get("customer", "").strip()
    try:
        amount = float(data.get("amount", 0))
    except Exception:
        amount = 0.0

    if not (username and customer and amount > 0):
        return jsonify({"error": "Missing fields"}), 400

    res = record_offline_payment(username, customer, amount)
    code = 200 if "success" in res else 400
    return jsonify(res), code
