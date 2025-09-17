from nest.core import Injectable
from datetime import datetime

@Injectable
class AppService:
    """
    Main application service that provides information about the scheduling system.
    """
    
    def __init__(self):
        self.app_name = "SchedulerApp"
        self.app_version = "1.0.0"
        self.description = "PyNest Application with Task Scheduling System"
        self.started_at = datetime.now()
    
    def get_app_info(self):
        """
        Returns detailed application information.
        """
        uptime = datetime.now() - self.started_at
        
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "description": self.description,
            "started_at": self.started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_formatted": str(uptime).split('.')[0],  # Remove microseconds
            "features": [
                "🕒 Task scheduling with @Cron",
                "⏰ Task scheduling with @Interval", 
                "📅 Predefined cron expressions",
                "🔄 Automatic integration with application lifecycle",
                "📊 Real-time task monitoring",
                "📝 Detailed execution logging"
            ],
            "endpoints": [
                {
                    "path": "/",
                    "method": "GET",
                    "description": "Application information"
                },
                {
                    "path": "/scheduler/stats",
                    "method": "GET", 
                    "description": "Scheduled tasks statistics"
                },
                {
                    "path": "/scheduler/logs",
                    "method": "GET",
                    "description": "Recent execution logs"
                },
                {
                    "path": "/health",
                    "method": "GET",
                    "description": "Application health check"
                }
            ],
            "scheduler_info": {
                "library": "APScheduler",
                "background_scheduler": True,
                "timezone": "UTC",
                "auto_start": True
            }
        }