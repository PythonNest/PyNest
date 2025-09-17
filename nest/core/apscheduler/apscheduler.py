from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

""" 
Instance of BackgroundScheduler from the APScheduler library.
Configured to initialize automatically and terminate properly.
"""

# Create scheduler instance
scheduler = BackgroundScheduler()
scheduler.configure(timezone=utc)

# Flag to control if scheduler has been started
_scheduler_started = False

def start_scheduler():
    """
    Starts the scheduler if it hasn't been started yet.
    """
    global _scheduler_started
    if not _scheduler_started and not scheduler.running:
        scheduler.start()
        _scheduler_started = True

def stop_scheduler():
    """
    Stops the scheduler safely.
    """
    global _scheduler_started
    if scheduler.running:
        scheduler.shutdown(wait=True)
        _scheduler_started = False

# Register shutdown function to be called when program ends
atexit.register(stop_scheduler)
