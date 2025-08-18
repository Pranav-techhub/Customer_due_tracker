# backend/services.py
from typing import Tuple
from backend.utils import (
    CUSTOMERS_CSV, DUES_CSV,
    read_csv, write_csv, log_action,
    generate_unique_username, generate_random_password
)
from backend.notifications.email_service import send_email


def create_customer_account(name: str, email: str, phone: str) -> Tuple[str, str]:
    if not name:
        raise ValueError("Name is required")

    username = generate_unique_username(name)
    password = generate_random_password()  # keep random generator

    customers = read_csv(CUSTOMERS_CSV)
    customers.append({
        "name": name.strip(),
        "email": (email or "").strip(),
        "phone": (phone or "").strip(),
        "username": username,
        "password": password
    })
    write_csv(CUSTOMERS_CSV, ["name", "email", "phone", "username", "password"], customers)

    # init dues if missing
    dues = read_csv(DUES_CSV)
    if not any(d.get("username") == username for d in dues):
        dues.append({"username": username, "customer": name, "due": "0"})
        write_csv(DUES_CSV, ["username", "customer", "due"], dues)

    log_action("create_customer", f"{username} ({name}) created")

    # optional email
    if email:
        send_email(
            email,
            "Your Account Details",
            f"<p>Hello {name},</p>"
            f"<p>Your account has been created.</p>"
            f"<p><b>Username:</b> {username}<br><b>Password:</b> {password}</p>"
        )

    return username, password


def change_password_service(username: str, old_password: str, new_password: str):
    customers = read_csv(CUSTOMERS_CSV)
    changed = False
    for c in customers:
        if c["username"] == username and c["password"] == old_password:
            c["password"] = new_password
            changed = True
            break
    if not changed:
        return {"error": "Invalid username or old password"}

    write_csv(CUSTOMERS_CSV, ["name", "email", "phone", "username", "password"], customers)
    log_action("change_password", f"{username} changed password")
    return {"success": True, "message": "Password updated"}


def record_offline_payment(username: str, customer: str, amount: float):
    if amount <= 0:
        return {"error": "Invalid amount"}

    dues = read_csv(DUES_CSV)
    for d in dues:
        if d["username"] == username:
            new_due = max(0.0, float(d.get("due", 0)) - amount)
            d["due"] = f"{new_due:.2f}"
            break
    write_csv(DUES_CSV, ["username", "customer", "due"], dues)
    log_action("offline_payment", f"{username} paid {amount} offline")
    return {"success": True}
