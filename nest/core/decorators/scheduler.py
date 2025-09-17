from typing import Optional, Callable, Union
from functools import wraps
import inspect
import weakref

from nest.core.apscheduler import scheduler, start_scheduler
from nest.core.apscheduler.enums.cron_expression import CronExpression
from nest.core.apscheduler.enums.scheduler_type import SchedulerTypes


# Global registry for scheduled methods and their instances
_scheduled_methods_registry = {}
_pending_scheduled_methods = []

def _execute_scheduled_method(instance_ref, method_name, *args, **kwargs):
    """
    Execute a scheduled method with the correct instance.
    """
    instance = instance_ref()
    if instance is None:
        return
    
    try:
        method = getattr(instance, method_name)
        return method(*args, **kwargs)
    except Exception as e:
        raise

def _register_pending_method(cls, method_name, job_config):
    """
    Register a method to be scheduled when an instance is created.
    """
    if cls not in _pending_scheduled_methods:
        _pending_scheduled_methods.append((cls, method_name, job_config))

def activate_scheduled_methods_for_instance(instance):
    """
    Activate all scheduled methods for a given instance.
    This is called automatically by PyNest when services are instantiated.
    """
    cls = instance.__class__
    
    # Check for scheduled methods in this class and its base classes
    for method_name in dir(instance):
        if method_name.startswith('_'):
            continue
            
        attr = getattr(cls, method_name, None)
        if isinstance(attr, ScheduledMethod):
            # Trigger the descriptor to schedule the method
            getattr(instance, method_name)

class ScheduledMethod:
    """
    Descriptor for scheduled methods that automatically schedules them when accessed.
    """
    def __init__(self, func, job_config):
        self.func = func
        self.job_config = job_config
        self.scheduled_instances = weakref.WeakSet()
        wraps(func)(self)
    
    def __set_name__(self, owner, name):
        self.name = name
        self.owner = owner
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        # Check if this method has already been scheduled for this instance
        if instance not in self.scheduled_instances:
            self._schedule_for_instance(instance)
            self.scheduled_instances.add(instance)
        
        return self.func.__get__(instance, owner)
    
    def _schedule_for_instance(self, instance):
        """
        Schedule the method for a specific instance.
        """
        job_id = f"{self.job_config['type']}_{instance.__class__.__module__}_{instance.__class__.__name__}_{self.func.__name__}_{id(instance)}"
        
        # Create weak reference to instance to avoid memory leaks
        instance_ref = weakref.ref(instance)
        
        # Create wrapper function that calls the method with correct instance
        def method_wrapper():
            return _execute_scheduled_method(instance_ref, self.func.__name__)
        
        method_wrapper.__name__ = f"{instance.__class__.__name__}.{self.func.__name__}"
        
        try:
            if self.job_config['type'] == 'cron':
                scheduler.add_job(
                    method_wrapper,
                    trigger=self.job_config['expression'].value,
                    id=job_id,
                    replace_existing=True,
                    name=f"Cron Task: {instance.__class__.__name__}.{self.func.__name__}"
                )
            
            elif self.job_config['type'] == 'interval':
                scheduler.add_job(
                    method_wrapper,
                    trigger='interval',
                    id=job_id,
                    replace_existing=True,
                    name=f"Interval Task: {instance.__class__.__name__}.{self.func.__name__}",
                    **self.job_config['trigger_kwargs']
                )
                
                # Create interval description for logging
                interval_desc = []
                if self.job_config['trigger_kwargs'].get('days'): 
                    interval_desc.append(f"{self.job_config['trigger_kwargs']['days']} days")
                if self.job_config['trigger_kwargs'].get('hours'): 
                    interval_desc.append(f"{self.job_config['trigger_kwargs']['hours']} hours")
                if self.job_config['trigger_kwargs'].get('minutes'): 
                    interval_desc.append(f"{self.job_config['trigger_kwargs']['minutes']} minutes")
                if self.job_config['trigger_kwargs'].get('seconds'): 
                    interval_desc.append(f"{self.job_config['trigger_kwargs']['seconds']} seconds")
                
            
            # Start scheduler if not running
            start_scheduler()
            
        except Exception as e:
            raise ValueError(f"Error scheduling method: {e}")

def Cron(expression: CronExpression = CronExpression.EVERY_MINUTE) -> Callable:
    """
    Decorator to schedule a function or method to execute at specific times using cron expressions.
    
    Args:
        expression (CronExpression): A predefined cron expression.
        
    Returns:
        Callable: The decorated function or method.
        
    Example:
        @Cron(expression=CronExpression.EVERY_MINUTE)
        def my_task():
            print("Running every minute")
            
        # Or in a class:
        class MyService:
            @Cron(expression=CronExpression.EVERY_MINUTE)
            def my_method(self):
                print("Method running every minute")
    """
    def decorator(func: Callable) -> Callable:
        # Validate if the expression is valid
        if not isinstance(expression, CronExpression):
            raise ValueError("Invalid cron expression.")
        
        # Check if it's a class method (has 'self' as first parameter)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        is_method = len(params) > 0 and params[0] == 'self'
        
        if is_method:
            # For class methods, return a ScheduledMethod
            return ScheduledMethod(func, {
                'type': 'cron',
                'expression': expression
            })
        else:
            # For standalone functions, schedule directly
            job_id = f"cron_{func.__module__}_{func.__name__}_{id(func)}"
            
            try:
                scheduler.add_job(
                    func,
                    trigger=expression.value,
                    id=job_id,
                    replace_existing=True,
                    name=f"Cron Task: {func.__name__}"
                )
                
                # Start scheduler if not running
                start_scheduler()
                
            except Exception as e:                
                raise ValueError(f"Error scheduling cron function: {e}")
            
            return func
    
    return decorator


def Interval(
    seconds: Optional[int] = None,
    minutes: Optional[int] = None, 
    hours: Optional[int] = None, 
    days: Optional[int] = None
) -> Callable:
    """
    Decorator to schedule a function or method to execute at regular intervals.
    
    Args:
        seconds (int, optional): Number of seconds between executions.
        minutes (int, optional): Number of minutes between executions.
        hours (int, optional): Number of hours between executions.
        days (int, optional): Number of days between executions.
        
    Returns:
        Callable: The decorated function or method.
        
    Example:
        @Interval(seconds=30)
        def my_task():
            print("Running every 30 seconds")
            
        # Or in a class:
        class MyService:
            @Interval(minutes=5)
            def my_method(self):
                print("Method running every 5 minutes")
    """
    def decorator(func: Callable) -> Callable:
        # Validate that at least one time parameter was provided
        if not any([seconds, minutes, hours, days]):
            raise ValueError("At least one time parameter must be provided.")
        
        # Prepare trigger parameters
        trigger_kwargs = {}
        if seconds is not None:
            trigger_kwargs['seconds'] = seconds
        if minutes is not None:
            trigger_kwargs['minutes'] = minutes
        if hours is not None:
            trigger_kwargs['hours'] = hours
        if days is not None:
            trigger_kwargs['days'] = days
        
        # Check if it's a class method (has 'self' as first parameter)
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        is_method = len(params) > 0 and params[0] == 'self'
        
        if is_method:
            # For class methods, return a ScheduledMethod
            return ScheduledMethod(func, {
                'type': 'interval',
                'trigger_kwargs': trigger_kwargs
            })
        else:
            # For standalone functions, schedule directly
            job_id = f"interval_{func.__module__}_{func.__name__}_{id(func)}"
            
            try:
                scheduler.add_job(
                    func,
                    trigger='interval',
                    id=job_id,
                    replace_existing=True,
                    name=f"Interval Task: {func.__name__}",
                    **trigger_kwargs
                )
                
                # Start scheduler if not running
                start_scheduler()
                
                # Create interval description for logging
                interval_desc = []
                if days: interval_desc.append(f"{days} days")
                if hours: interval_desc.append(f"{hours} hours")
                if minutes: interval_desc.append(f"{minutes} minutes")
                if seconds: interval_desc.append(f"{seconds} seconds")
                
            except Exception as e:                
                raise ValueError(f"Error scheduling interval function: {e}")
            
            return func
    
    return decorator