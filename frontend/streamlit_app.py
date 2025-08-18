import streamlit as st
import pandas as pd
import requests
import os
from pathlib import Path

# ----------------- CONFIG -----------------
API_URL = os.getenv("API_URL", "http://localhost:5000")
CUSTOMERS_CSV = Path(__file__).parent.parent / "backend" / "data" / "customers.csv"

st.set_page_config(page_title="Customer Due Tracker", layout="wide")

# Apply custom CSS for better fonts in light theme
st.markdown("""
    <style>
    body, input, textarea, select, button {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: 15px !important;
        color: #111111 !important;
    }
    .stSidebar, .css-1d391kg {
        font-size: 15px !important;
        font-weight: 500;
    }
    h1, h2, h3 {
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)


# ----------------- HELPERS -----------------
def load_customers():
    if not CUSTOMERS_CSV.exists():
        return pd.DataFrame(columns=["email", "password", "name", "dues"])
    return pd.read_csv(CUSTOMERS_CSV)


def save_customers(df):
    df.to_csv(CUSTOMERS_CSV, index=False)


def authenticate_user(username, password, role):
    if role == "owner":
        return username == os.getenv("OWNER_USERNAME", "admin") and password == os.getenv("OWNER_PASSWORD", "admin")
    elif role == "customer":
        df = load_customers()
        user = df[(df["email"] == username) & (df["password"] == password)]
        return not user.empty
    return False


# ----------------- LOGIN -----------------
def login():
    st.title("🔐 Customer Due Tracking System")

    role = st.radio("Login as:", ["Owner", "Customer"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(username, password, role.lower()):
            st.session_state["role"] = role.lower()
            st.session_state["username"] = username
            st.session_state["logged_in"] = True
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

# ----------------- OWNER INTERFACE -----------------
def owner_dashboard():
    st.title("👑 Owner Dashboard")

    # Razorpay Keys
    st.subheader("Razorpay Settings")
    mode = st.radio("Mode", ["Test", "Live"], horizontal=True)
    key_id = st.text_input("Razorpay Key ID", type="password")
    key_secret = st.text_input("Razorpay Key Secret", type="password")
    if st.button("Save Razorpay Keys"):
        st.session_state["razorpay"] = {
            "mode": mode,
            "key_id": key_id,
            "key_secret": key_secret
        }
        st.success("Razorpay keys saved in session.")

    # Manage Customers
    st.subheader("Customer Management")
    df = load_customers()
    st.dataframe(df)

# ----------------- CUSTOMER INTERFACE -----------------
def customer_dashboard():
    df = load_customers()
    user = df[df["email"] == st.session_state["username"]].iloc[0]

    st.title(f"👤 Welcome {user['name']}")

    # Show dues
    st.metric("Your Current Due", f"₹{user['dues']}")

    # Payment section
    st.subheader("💳 Pay Your Due")
    upi_id = st.text_input("Enter your UPI ID")
    amount = st.number_input("Amount to Pay", min_value=1, max_value=int(user["dues"]), value=1)

    if st.button("Pay"):
        if "razorpay" not in st.session_state:
            st.error("Owner has not configured Razorpay keys yet.")
        elif not upi_id:
            st.warning("Enter a valid UPI ID.")
        else:
            st.info("Sending payment request...")
            # In real integration, we call backend Razorpay API here
            # For now, we simulate success
            df.loc[df["email"] == user["email"], "dues"] = int(user["dues"]) - amount
            save_customers(df)
            st.success(f"Payment of ₹{amount} successful! Your new due is ₹{int(user['dues']) - amount}")

    # Password change
    st.subheader("🔑 Change Password")
    old_pwd = st.text_input("Old Password", type="password")
    new_pwd = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        if old_pwd != user["password"]:
            st.error("Old password is incorrect.")
        elif not new_pwd.strip():
            st.error("New password cannot be empty.")
        else:
            df.loc[df["email"] == user["email"], "password"] = new_pwd
            save_customers(df)
            st.success("Password updated successfully!")

# ----------------- MAIN -----------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    if st.session_state["role"] == "owner":
        owner_dashboard()
    elif st.session_state["role"] == "customer":
        customer_dashboard()
                df = load_customers()
                if email in df["email"].values:
                    st.error("Customer with this email already exists")
                else:
                    password = generate_password()
                    new_row = pd.DataFrame([{"name": name, "email": email, "password": hash_password(password)}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_customers(df)
                    st.success(f"Customer created. Username = {email}, Password = {password}")
            else:
                st.error("All fields required")

    elif menu == "View Customers":
        st.subheader("All Customers")
        st.dataframe(load_customers())

    elif menu == "Manage Dues":
        st.subheader("Manage Dues")
        df = load_dues()
        st.dataframe(df)

    elif menu == "Razorpay Settings":
        st.subheader("Razorpay API Keys")
        mode = st.radio("Mode", ["test", "live"])
        key_id = st.text_input("Key ID", value=st.session_state.razorpay_keys.get("key_id", ""))
        key_secret = st.text_input("Key Secret", value=st.session_state.razorpay_keys.get("key_secret", ""), type="password")

        if st.button("Save Keys"):
            st.session_state.razorpay_keys = {"mode": mode, "key_id": key_id, "key_secret": key_secret}
            st.success("Razorpay keys saved for session")

# ------------------ Customer Interface ------------------
elif st.session_state.role == "customer":
    st.sidebar.title("Customer Dashboard")
    menu = st.sidebar.radio("Menu", ["My Dues", "Pay Due", "Transactions", "Change Password"])

    if menu == "My Dues":
        st.subheader("My Dues")
        df = load_dues()
        my_dues = df[df["email"] == st.session_state.customer_email]
        if not my_dues.empty:
            st.dataframe(my_dues)
        else:
            st.info("No dues found")

    elif menu == "Pay Due":
        st.subheader("Pay Dues")
        df_dues = load_dues()
        my_due = df_dues[df_dues["email"] == st.session_state.customer_email]
        if not my_due.empty:
            amount_due = my_due.iloc[0]["amount"]
            st.write(f"Your current due: ₹{amount_due}")

            pay_amount = st.number_input("Enter amount to pay", min_value=1, max_value=int(amount_due), value=int(amount_due))
            upi_id = st.text_input("Enter your UPI ID")

            if st.button("Pay Now"):
                keys = st.session_state.razorpay_keys
                if not keys["key_id"] or not keys["key_secret"]:
                    st.error("Owner has not configured Razorpay keys")
                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/payments/create",
                            json={
                                "key_id": keys["key_id"],
                                "key_secret": keys["key_secret"],
                                "amount": pay_amount,
                                "upi_id": upi_id
                            }
                        ).json()

                        if response.get("success"):
                            st.success("Payment successful via Razorpay")

                            # Update due
                            df_dues.loc[df_dues["email"] == st.session_state.customer_email, "amount"] -= pay_amount
                            save_dues(df_dues)

                            # Log transaction
                            df_txn = load_transactions()
                            new_txn = pd.DataFrame([{
                                "email": st.session_state.customer_email,
                                "amount": pay_amount,
                                "method": "UPI",
                                "status": "Paid"
                            }])
                            df_txn = pd.concat([df_txn, new_txn], ignore_index=True)
                            save_transactions(df_txn)
                        else:
                            st.error(f"Payment failed: {response.get('error')}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    elif menu == "Transactions":
        st.subheader("My Transactions")
        df = load_transactions()
        my_txns = df[df["email"] == st.session_state.customer_email]
        if not my_txns.empty:
            st.dataframe(my_txns)
        else:
            st.info("No transactions found")

    elif menu == "Change Password":
        st.subheader("Change My Password")
        old_pw = st.text_input("Old Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        if st.button("Update Password"):
            df = load_customers()
            user = df[df["email"] == st.session_state.customer_email]
            if not user.empty and user.iloc[0]["password"] == hash_password(old_pw):
                df.loc[df["email"] == st.session_state.customer_email, "password"] = hash_password(new_pw)
                save_customers(df)
                st.success("Password updated successfully")
            else:
                st.error("Old password is incorrect")
                    st.info("🧪 Use test UPI like `success@razorpay` in Razorpay’s test flow to simulate success.")

                # Simulated confirmation for testing (replace with webhook in prod)
                confirm = requests.post(f"{API_URL}/confirm_payment", json={
                    "order_id": order["order_id"],
                    "amount": amount,
                    "customer_name": customer_name,
                    "username": username,
                    "mode": st.session_state["mode"]
                })
                if confirm.status_code == 200:
                    st.success("🎉 Payment confirmed & dues updated.")
                else:
                    st.warning("Payment not confirmed. Please try again.")
            else:
                st.error(r.json().get("error", "Failed to create order"))
        except Exception as e:
            st.error(f"Request failed: {e}")

st.markdown("---")

with st.expander("ℹ️ How to test payments"):
    st.write("""
- Set **Mode = Test** and save your **Test Key ID/Secret** and **Owner UPI**.
- Click **Pay Now** with any amount.
- This demo calls `/confirm_payment` right away to simulate success and update dues.
- For production, set up **Razorpay Webhooks** and only update dues after authenticating the webhook signature.
""")
