"""
Script: Task Scheduler
What it does: Runs a function automatically at a set time interval.
Useful for tasks that need to run periodically — like backups, checks, or reports.

Install: pip install schedule
"""

import time
import datetime

try:
    import schedule  # simple job scheduling library

    # Define the tasks to run
    def morning_report():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Good morning! Running morning report...")

    def check_system():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Checking system status... All OK!")

    def save_backup():
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Saving backup... Done!")

    # Schedule the tasks
    schedule.every(5).seconds.do(check_system)    # every 5 seconds
    schedule.every(10).seconds.do(save_backup)    # every 10 seconds
    schedule.every().day.at("09:00").do(morning_report)  # every day at 9 AM

    print("Scheduler started. Running for 20 seconds...")
    print("(In real use, this would run forever with a while True loop)\n")

    # Run the scheduler for 20 seconds as a demo
    start = time.time()
    while time.time() - start < 20:
        schedule.run_pending()  # check and run any due tasks
        time.sleep(1)           # wait 1 second before checking again

    print("\nScheduler demo complete.")

except ImportError:
    print("schedule not installed. Run: pip install schedule")
    print("\nAlternatively, use Python's built-in time module:")

    # Simple manual scheduling without external library
    def simple_task():
        print(f"Task ran at: {datetime.datetime.now()}")

    print("\nRunning simple task every 3 seconds for 9 seconds:")
    for _ in range(3):
        simple_task()
        time.sleep(3)
