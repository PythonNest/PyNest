from nest.core import Injectable
from nest.core.decorators.scheduler import Cron, Interval
from nest.core.apscheduler.enums.cron_expression import CronExpression
from nest.core.apscheduler import scheduler
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@Injectable
class SchedulerService:
    """
    Service that demonstrates the use of task scheduling decorators.
    
    This service contains examples of scheduled tasks using:
    - @Cron: for tasks based on cron expressions
    - @Interval: for tasks that run at regular intervals
    """
    
    def __init__(self):
        self.execution_count = 0
        self.task_logs = []
        logger.info("SchedulerService initialized - scheduled methods will be activated automatically by PyNest")
    
    @Interval(seconds=10)
    def task_every_10_seconds(self):
        """
        Task that runs every 10 seconds for quick demonstration.
        """
        self.execution_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] Task executed every 10 seconds - Execution #{self.execution_count}"
        
        self.task_logs.append({
            "task": "task_every_10_seconds",
            "timestamp": timestamp,
            "execution_number": self.execution_count
        })
        
        # Keep only the last 10 logs
        if len(self.task_logs) > 10:
            self.task_logs = self.task_logs[-10:]
        
        logger.info(message)
        print(message)  # For console visualization
        return message
    
    @Cron(expression=CronExpression.EVERY_MINUTE)
    def task_every_minute(self):
        """
        Task that runs every minute using cron expression.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] Cron task executed - EVERY_MINUTE"
        
        self.task_logs.append({
            "task": "task_every_minute",
            "timestamp": timestamp,
            "type": "cron"
        })
        
        logger.info(message)
        print(message)
        return message
    
    @Cron(expression=CronExpression.EVERY_30_SECONDS)
    def task_every_30_seconds_cron(self):
        """
        Task that runs every 30 seconds using cron expression.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] Cron task executed - EVERY_30_SECONDS"
        
        self.task_logs.append({
            "task": "task_every_30_seconds_cron", 
            "timestamp": timestamp,
            "type": "cron"
        })
        
        logger.info(message)
        print(message)
        return message
    
    @Interval(minutes=1)
    def task_every_minute_interval(self):
        """
        Task that runs every minute using interval.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = f"[{timestamp}] Interval task executed - every 1 minute"
        
        self.task_logs.append({
            "task": "task_every_minute_interval",
            "timestamp": timestamp,
            "type": "interval"
        })
        
        logger.info(message)
        print(message)
        return message
    
    def get_statistics(self):
        """
        Returns statistics of scheduled tasks.
        """
        # Get information from active scheduler jobs
        jobs_info = []
        for job in scheduler.get_jobs():
            jobs_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "execution_count": self.execution_count,
            "active_jobs": len(scheduler.get_jobs()),
            "scheduler_running": scheduler.running,
            "jobs_details": jobs_info,
            "recent_logs": self.task_logs[-5:],  # Last 5 logs
            "scheduled_tasks": [
                {
                    "name": "task_every_10_seconds",
                    "type": "interval", 
                    "description": "Runs every 10 seconds"
                },
                {
                    "name": "task_every_minute",
                    "type": "cron",
                    "description": "Runs every minute (cron)"
                },
                {
                    "name": "task_every_30_seconds_cron",
                    "type": "cron", 
                    "description": "Runs every 30 seconds (cron)"
                },
                {
                    "name": "task_every_minute_interval",
                    "type": "interval",
                    "description": "Runs every minute (interval)"
                }
            ]
        }
    
    def get_recent_logs(self):
        """
        Returns recent logs of task executions.
        """
        return {
            "total_executions": self.execution_count,
            "recent_logs": self.task_logs,
            "scheduler_status": {
                "running": scheduler.running,
                "jobs_count": len(scheduler.get_jobs())
            }
        }