"""
Optional simple scheduler (run separately if you want periodic jobs).
Example: send reminders for high dues.
"""
import time
import schedule
from backend.services import send_email  # if you add scheduled emails

def main():
    # schedule.every().day.at("09:00").do(your_job)
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
