import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Get values from .env
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_NAME = os.getenv("FROM_NAME")

# Debug print to check if .env loaded correctly
print("Loaded EMAIL_ADDRESS:", EMAIL_ADDRESS)
print("Loaded EMAIL_PASSWORD:", EMAIL_PASSWORD)

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = f"{FROM_NAME} <{EMAIL_ADDRESS}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# Test sending
send_email("sumeetkamble0116@gmail.com", "Test Email from Flask", "Hello! This is a test email.")
