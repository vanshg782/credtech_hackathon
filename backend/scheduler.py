from apscheduler.schedulers.background import BackgroundScheduler
import time

scheduler = BackgroundScheduler()

def sample_job():
    print(f"[Scheduler] Job executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

def start_scheduler():
    # Add a simple repeating job (every 10 seconds)
    scheduler.add_job(sample_job, "interval", seconds=10, id="sample_job", replace_existing=True)
    scheduler.start()
    print("[Scheduler] Started background scheduler")
