"""
Optional simple scheduler (run separately if you want periodic jobs).
Example: send reminders for high dues.
"""
import time
import schedule
from pathlib import Path
from backend.services import send_due_reminders

def main():
    schedule.every().day.at("09:00").do(send_due_reminders)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
