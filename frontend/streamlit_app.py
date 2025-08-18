# frontend/streamlit_app.py
import os
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:5000/api")

st.set_page_config(page_title="Customer Due Tracker", page_icon="💰", layout="centered")

# ---------- Typography only (no background changes) ----------
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
    color: #202020;
    font-size: 16px;
}
h1 { font-size: 2.2rem !important; font-weight: 700; color: #111111; }
h2 { font-size: 1.8rem !important; font-weight: 600; color: #222222; }
h3 { font-size: 1.4rem !important; font-weight: 600; color: #333333; }
</style>
""", unsafe_allow_html=True)

st.title("💰 Customer Due Tracking System")

# ---------------- Admin Payment Settings ----------------
st.sidebar.title("⚙️ Admin Settings")
with st.sidebar.expander("🔑 Payment Configuration", expanded=True):
    mode = st.radio("Mode", ["Test", "Live"], index=0, horizontal=True)
    razorpay_key_id = st.text_input("Razorpay Key ID", type="password")
    razorpay_key_secret = st.text_input("Razorpay Key Secret", type="password")
    owner_upi_id = st.text_input("Owner UPI ID (destination)")

    if st.button("Save Payment Settings"):
        if razorpay_key_id and razorpay_key_secret and owner_upi_id:
            st.session_state["mode"] = mode.lower()
            st.session_state["razorpay_key_id"] = razorpay_key_id
            st.session_state["razorpay_key_secret"] = razorpay_key_secret
            st.session_state["owner_upi_id"] = owner_upi_id
            st.success(f"✅ Payment settings saved for this session ({mode} Mode)")
            if st.session_state["mode"] == "test":
                st.info("🧪 In Test Mode use Razorpay test UPI such as `success@razorpay` to simulate success.")
        else:
            st.warning("⚠️ Please fill all fields before saving.")

st.markdown("---")

# ---------------- Customer: Change Password ----------------
st.header("🔑 Change Password")
cp_col1, cp_col2 = st.columns(2)
with cp_col1:
    cp_username = st.text_input("Username")
    cp_old = st.text_input("Old Password", type="password")
with cp_col2:
    cp_new = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        if cp_username and cp_old and cp_new:
            try:
                r = requests.post(f"{API_URL}/change_password", json={
                    "username": cp_username,
                    "old_password": cp_old,
                    "new_password": cp_new
                })
                if r.status_code == 200:
                    st.success("✅ Password updated successfully.")
                else:
                    st.error(r.json().get("error", "Failed"))
            except Exception as e:
                st.error(f"Request failed: {e}")
        else:
            st.warning("Please complete all fields.")

st.markdown("---")

# ---------------- Customer: Make a Payment ----------------
st.header("💳 Make a Payment")
username = st.text_input("Your Username")
customer_name = st.text_input("Your Registered Name")
amount = st.number_input("Amount to pay (INR)", min_value=1, step=1)

if st.button("Pay Now"):
    # Validate owner settings
    required = ("mode" in st.session_state and
                "razorpay_key_id" in st.session_state and
                "razorpay_key_secret" in st.session_state and
                "owner_upi_id" in st.session_state)

    if not required:
        st.error("❌ Owner has not configured payment settings yet.")
    elif not (username and customer_name and amount > 0):
        st.error("❌ Please enter username, registered name, and amount.")
    else:
        payload = {
            "amount": amount,
            "mode": st.session_state["mode"],
            "key_id": st.session_state["razorpay_key_id"],
            "key_secret": st.session_state["razorpay_key_secret"],
            "upi_id": st.session_state["owner_upi_id"],
            "customer_name": customer_name,
            "username": username
        }
        try:
            r = requests.post(f"{API_URL}/create_order", json=payload)
            if r.status_code == 200:
                order = r.json()
                st.success(f"✅ Order created: {order['order_id']}")
                if st.session_state["mode"] == "test":
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
