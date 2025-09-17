from nest.core import Controller, Get
from .app_service import AppService
from .scheduler_service import SchedulerService

@Controller("/")
class AppController:
    """
    Main application controller with endpoints to monitor scheduled tasks.
    """
    
    def __init__(self, app_service: AppService, scheduler_service: SchedulerService):
        self.app_service = app_service
        self.scheduler_service = scheduler_service
    
    @Get("/")
    def get_app_info(self):
        """
        Returns application information.
        """
        return self.app_service.get_app_info()
    
    @Get("/scheduler/stats")
    def get_scheduler_stats(self):
        """
        Returns statistics of scheduled tasks.
        """
        return self.scheduler_service.get_statistics()
    
    @Get("/scheduler/logs")
    def get_scheduler_logs(self):
        """
        Returns recent logs of task executions.
        """
        return self.scheduler_service.get_recent_logs()
    
    @Get("/health")
    def health_check(self):
        """
        Health check endpoint for application and scheduler.
        """
        from nest.core.apscheduler import scheduler
        
        return {
            "status": "healthy",
            "scheduler_running": scheduler.running,
            "active_jobs": len(scheduler.get_jobs()),
            "app_info": self.app_service.get_app_info()
        }