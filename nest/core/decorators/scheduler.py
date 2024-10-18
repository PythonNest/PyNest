from typing import Optional, Callable, Type

from nest.core.apscheduler import scheduler


from nest.core.apscheduler.enums.cron_expression import CronExpression
from nest.core.apscheduler.enums.scheduler_type import SchedulerType

def Cron(expression: CronExpression = CronExpression.EVERY_MINUTE) -> Callable:
    """
    Decorator that schedules a function to run at a specific time.

    Args:
        expression (CronExpression): A cron expression.

    Returns:
        function: The decorated function.
    """
    def decorated(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            """ 
            Wrapper function that schedules the function to run at a specific time.
            """
            try:
                if not isinstance(expression, CronExpression):
                    raise ValueError("Invalid cron expression.")
                scheduler.add_job(
                    func,
                    trigger = expression.value,
                    id = func.__name__,                    
                )
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {e}")
        
        
        return wrapper
    
    return decorated

def Interval(seconds: Optional[int] = 10, minutes: Optional[int] = None, hours: Optional[int] = None, days: Optional[int] = None) -> Callable:
    """
    Decorator that schedules a function to run at a specific interval.

    Args:
        seconds (int): The number of seconds between each run.
        minutes (int): The number of minutes between each run.
        hours (int): The number of hours between each run.
        days (int): The number of days between each run.

    Returns:
        function: The decorated function.
    """
    def decorated(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            """ 
            Wrapper function that schedules the function to run at a specific interval.
            """
            try:
                scheduler.add_job(
                    func,
                    trigger = SchedulerType.INTERVAL.value,
                    seconds = seconds,
                    minutes = minutes,
                    hours = hours,
                    days = days,
                    id = func.__name__
                )
            except Exception as e:
                raise ValueError(f"Invalid interval: {e}")
        
        return wrapper
    
    return decorated