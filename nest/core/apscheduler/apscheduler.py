from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler

""" 
An instance of the BackgroundScheduler class from the APScheduler library.
"""

scheduler = BackgroundScheduler()
scheduler.configure(timezone=utc)
