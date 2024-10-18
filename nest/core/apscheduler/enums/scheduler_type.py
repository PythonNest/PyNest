from enum import Enum

class SchedulerTypes(Enum):
    """ 
    An enumeration of scheduler types.
    """
    CRON = 'cron',
    DATE = 'date'
    INTERVAL = 'interval',
    