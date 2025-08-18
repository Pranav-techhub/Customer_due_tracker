import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from os import getenv
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(getenv("SMTP_PORT", "587"))
SMTP_USER = getenv("SMTP_USER", "")
SMTP_PASS = getenv("SMTP_PASS", "")
FROM_EMAIL = getenv("FROM_EMAIL", SMTP_USER or "no-reply@example.com")

def send_email(to_email: str, subject: str, body: str) -> bool:
    if not (SMTP_USER and SMTP_PASS and to_email):
        # Not configured; treat as no-op success to avoid breaking flows
        return True

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Customer Due Tracker", FROM_EMAIL))
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        return True
    except Exception:
        return False
