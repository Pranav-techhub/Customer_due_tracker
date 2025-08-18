import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:5000")

# ---------------- Helper Functions ----------------
def load_customers():
    response = requests.get(f"{API_URL}/customers")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

def load_dues():
    response = requests.get(f"{API_URL}/dues")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

def load_transactions():
    response = requests.get(f"{API_URL}/transactions")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

def add_customer(name, email, due):
    response = requests.post(f"{API_URL}/customers", json={"name": name, "email": email, "due": due})
    return response

def record_payment(customer_id, amount, method="online"):
    response = requests.post(f"{API_URL}/pay", json={"customer_id": customer_id, "amount": amount, "method": method})
    return response

def change_customer_password(email, new_password):
    response = requests.post(f"{API_URL}/change_password", json={"email": email, "new_password": new_password})
    return response

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="Customer Due Tracker", layout="wide")

# Login Section
if "role" not in st.session_state:
    st.session_state.role = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

st.title("💰 Customer Due Tracking System")

if st.session_state.role is None:
    st.subheader("Login")
    role = st.selectbox("Login as", ["Owner", "Customer"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if role == "Owner" and username == "admin" and password == "admin":
            st.session_state.role = "owner"
        else:
            # For customers, backend validates
            response = requests.post(f"{API_URL}/login", json={"email": username, "password": password})
            if response.status_code == 200:
                st.session_state.role = "customer"
                st.session_state.user_email = username
            else:
                st.error("Invalid credentials")

# Owner Interface
elif st.session_state.role == "owner":
    menu = ["Dashboard", "Manage Customers", "Transactions", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Dashboard":
        st.subheader("📊 Dashboard")
        df_customers = load_customers()
        st.metric("Total Customers", len(df_customers))
        df_dues = load_dues()
        st.metric("Total Dues", df_dues["amount"].sum() if not df_dues.empty else 0.0)

    elif choice == "Manage Customers":
        st.subheader("Customer Management")
        df = load_customers()
        st.dataframe(df)

        with st.form("add_customer_form"):
            name = st.text_input("Customer Name")
            email = st.text_input("Customer Email")
            due = st.number_input("Initial Due Amount", min_value=0.0, step=0.1)
            submitted = st.form_submit_button("Add Customer")
            if submitted:
                if name and email:
                    add_customer(name, email, due)
                    st.success("Customer added successfully!")
                else:
                    st.error("Please provide both name and email")

    elif choice == "Transactions":
        st.subheader("Transaction History")
        df = load_transactions()
        st.dataframe(df)

    elif choice == "Logout":
        st.session_state.role = None
        st.session_state.user_email = None
        st.experimental_rerun()

# Customer Interface
elif st.session_state.role == "customer":
    menu = ["My Dues", "Make Payment", "Transactions", "Change Password", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "My Dues":
        st.subheader("My Dues")
        df_dues = load_dues()
        my_dues = df_dues[df_dues["email"] == st.session_state.user_email]
        st.dataframe(my_dues)

    elif choice == "Make Payment":
        st.subheader("Pay Due")
        df_dues = load_dues()
        my_dues = df_dues[df_dues["email"] == st.session_state.user_email]
        if not my_dues.empty:
            amount = st.number_input("Enter Amount", min_value=0.0, step=0.1)
            if st.button("Pay"):
                resp = record_payment(my_dues.iloc[0]["customer_id"], amount)
                if resp.status_code == 200:
                    st.success("Payment recorded successfully!")
                else:
                    st.error("Payment failed")
        else:
            st.info("No dues available")

    elif choice == "Transactions":
        st.subheader("My Transactions")
        df = load_transactions()
        my_txns = df[df["email"] == st.session_state.user_email]
        st.dataframe(my_txns)

    elif choice == "Change Password":
        st.subheader("Change Password")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Update Password"):
            resp = change_customer_password(st.session_state.user_email, new_pass)
            if resp.status_code == 200:
                st.success("Password updated successfully!")
            else:
                st.error("Failed to update password")

    elif choice == "Logout":
        st.session_state.role = None
        st.session_state.user_email = None
        st.experimental_rerun()
