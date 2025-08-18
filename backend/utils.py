import csv
import re
import random
import string
from pathlib import Path
from datetime import datetime

DATA_PATH = Path(__file__).parent / "data"
DATA_PATH.mkdir(parents=True, exist_ok=True)

CUSTOMERS_CSV = DATA_PATH / "customers.csv"
DUES_CSV = DATA_PATH / "dues.csv"
LOGS_CSV = DATA_PATH / "logs.csv"
TRANSACTIONS_CSV = DATA_PATH / "transactions.csv"

# ---------- CSV Helpers ----------

def ensure_csv(file: Path, fieldnames: list):
    if not file.exists():
        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

def ensure_headers(file: Path):
    if file == CUSTOMERS_CSV:
        ensure_csv(file, ["name", "email", "phone", "username", "password"])
    elif file == DUES_CSV:
        ensure_csv(file, ["username", "customer", "due"])
    elif file == LOGS_CSV:
        ensure_csv(file, ["timestamp", "action", "details"])
    elif file == TRANSACTIONS_CSV:
        ensure_csv(file, ["date", "username", "customer", "amount", "order_id", "status", "mode"])

def read_csv(file: Path):
    ensure_headers(file)
    with open(file, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(file: Path, fieldnames: list, rows: list):
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def append_csv(file: Path, fieldnames: list, row: dict):
    rows = read_csv(file)
    rows.append(row)
    write_csv(file, fieldnames, rows)

def log_action(action: str, details: str):
    ensure_headers(LOGS_CSV)
    append_csv(LOGS_CSV, ["timestamp", "action", "details"], {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "details": details
    })

# ---------- Username & Password ----------

def clean_username_from_name(name: str) -> str:
    base = re.sub(r'[^a-zA-Z0-9]', '', (name or "")).lower()
    return base or "user"

def generate_unique_username(name: str) -> str:
    users = read_csv(CUSTOMERS_CSV)
    existing = {u["username"].lower() for u in users if u.get("username")}
    base = clean_username_from_name(name)
    username = base
    i = 1
    while username.lower() in existing:
        username = f"{base}{i}"
        i += 1
    return username

def generate_random_password(length: int = 10) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))
