import streamlit as st
import pandas as pd
import requests
import hashlib
from pathlib import Path
import random
import string

# ------------------ Config ------------------
API_URL = "http://localhost:5000"   # Flask backend

CUSTOMERS_CSV = Path(__file__).parent.parent / "backend" / "data" / "customers.csv"
DUES_CSV = Path(__file__).parent.parent / "backend" / "data" / "dues.csv"
TRANSACTIONS_CSV = Path(__file__).parent.parent / "backend" / "data" / "transactions.csv"

OWNER_USERNAME = "owner"
OWNER_PASSWORD = "owner123"   # example; in real app keep in .env

# ------------------ Helpers ------------------
def load_customers():
    return pd.read_csv(CUSTOMERS_CSV)

def save_customers(df):
    df.to_csv(CUSTOMERS_CSV, index=False)

def load_dues():
    return pd.read_csv(DUES_CSV)

def save_dues(df):
    df.to_csv(DUES_CSV, index=False)

def load_transactions():
    return pd.read_csv(TRANSACTIONS_CSV)

def save_transactions(df):
    df.to_csv(TRANSACTIONS_CSV, index=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# ------------------ UI Styling ------------------
st.markdown(
    """
    <style>
    .stApp { font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3, h4 { color: #222; font-weight: 600; }
    .stSidebar { font-size: 16px; }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ Authentication ------------------
if "role" not in st.session_state:
    st.session_state.role = None
if "customer_email" not in st.session_state:
    st.session_state.customer_email = None
if "razorpay_keys" not in st.session_state:
    st.session_state.razorpay_keys = {"mode": "test", "key_id": "", "key_secret": ""}

st.title("💰 Customer Due Tracking System")

# ------------------ Login ------------------
if st.session_state.role is None:
    st.subheader("Login")

    role = st.radio("Login as:", ["Owner", "Customer"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if role == "Owner":
            if username == OWNER_USERNAME and password == OWNER_PASSWORD:
                st.session_state.role = "owner"
                st.success("Owner login successful")
            else:
                st.error("Invalid owner credentials")
        else:  # Customer
            df = load_customers()
            user = df[df["email"] == username]
            if not user.empty:
                stored_hash = user.iloc[0]["password"]
                if stored_hash == hash_password(password):
                    st.session_state.role = "customer"
                    st.session_state.customer_email = username
                    st.success("Customer login successful")
                else:
                    st.error("Wrong password")
            else:
                st.error("No customer with this email found")

# ------------------ Owner Interface ------------------
elif st.session_state.role == "owner":
    st.sidebar.title("Owner Dashboard")
    menu = st.sidebar.radio("Menu", ["Add Customer", "View Customers", "Manage Dues", "Razorpay Settings"])

    if menu == "Add Customer":
        st.subheader("Add New Customer")
        name = st.text_input("Customer Name")
        email = st.text_input("Customer Email")
        if st.button("Create Customer"):
            if name and email:
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
