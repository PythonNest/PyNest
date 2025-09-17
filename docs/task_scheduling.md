# Task Scheduling in PyNest ⏰

## Introduction

PyNest provides a robust task scheduling system using the APScheduler library. This feature enables you to execute functions at specific times or regular intervals, making it perfect for background tasks, periodic reports, data cleanup, and automated operations. The scheduling system integrates seamlessly with PyNest's dependency injection and module system.

## Defining Scheduled Tasks

PyNest offers two main decorators for task scheduling: `@Cron` for time-based scheduling and `@Interval` for interval-based execution.

### @Cron Decorator

The `@Cron` decorator allows you to schedule tasks using predefined cron expressions. It works with both standalone functions and class methods.

```python
from nest.core.decorators.scheduler import Cron
from nest.core.apscheduler.enums.cron_expression import CronExpression

@Cron(expression=CronExpression.EVERY_DAY_AT_MIDNIGHT)
def daily_cleanup():
    """Execute daily cleanup at midnight."""
    print("Running daily cleanup...")

@Cron(expression=CronExpression.EVERY_WEEKDAY)
def weekday_report():
    """Generate reports on weekdays."""
    print("Generating weekday report...")
```

### @Interval Decorator

The `@Interval` decorator schedules tasks to run at regular intervals. You can specify intervals using seconds, minutes, hours, or days.

```python
from nest.core.decorators.scheduler import Interval

@Interval(minutes=5)
def health_check():
    """Check system health every 5 minutes."""
    print("Performing health check...")

@Interval(hours=2)
def cache_refresh():
    """Refresh cache every 2 hours."""
    print("Refreshing cache...")
```

## Predefined Cron Expressions

PyNest provides a comprehensive set of predefined cron expressions for common scheduling needs:

**Time Intervals:**
- `EVERY_SECOND`, `EVERY_5_SECONDS`, `EVERY_30_SECONDS`
- `EVERY_MINUTE`, `EVERY_5_MINUTES`, `EVERY_30_MINUTES`
- `EVERY_HOUR`, `EVERY_2_HOURS`, `EVERY_6_HOURS`, `EVERY_12_HOURS`

**Daily Schedules:**
- `EVERY_DAY_AT_MIDNIGHT`, `EVERY_DAY_AT_NOON`
- `EVERY_DAY_AT_1AM`, `EVERY_DAY_AT_6PM`

**Weekly Schedules:**
- `EVERY_WEEK`, `EVERY_WEEKDAY`, `EVERY_WEEKEND`
- `MONDAY_TO_FRIDAY_AT_9AM`, `MONDAY_TO_FRIDAY_AT_5PM`

**Monthly and Yearly:**
- `EVERY_1ST_DAY_OF_MONTH_AT_MIDNIGHT`
- `EVERY_QUARTER`, `EVERY_6_MONTHS`, `EVERY_YEAR`

## Using Scheduled Tasks in Services

The scheduling decorators integrate seamlessly with PyNest's dependency injection system. When you decorate methods in an `@Injectable` service, PyNest automatically detects and schedules them during application startup.

### Basic Service with Scheduling

```python
from nest.core import Injectable
from nest.core.decorators.scheduler import Cron, Interval
from nest.core.apscheduler.enums.cron_expression import CronExpression
import logging

@Injectable
class TaskService:
    def __init__(self):
        self.execution_count = 0
        logging.info("TaskService initialized - scheduled methods activated automatically")
    
    @Cron(expression=CronExpression.EVERY_DAY_AT_MIDNIGHT)
    def daily_cleanup(self):
        """Execute daily cleanup at midnight."""
        self.execution_count += 1
        logging.info(f"Daily cleanup executed #{self.execution_count}")
        
        # Cleanup logic here
        return f"Cleanup completed - execution #{self.execution_count}"
    
    @Interval(minutes=5)
    def health_check(self):
        """Perform health check every 5 minutes."""
        logging.info("Performing system health check")
        
        # Health check logic here
        return "System healthy"
```

### Dependency Injection with Scheduled Tasks

```python
from nest.core import Injectable
from nest.core.decorators.scheduler import Cron
from nest.core.apscheduler.enums.cron_expression import CronExpression

@Injectable
class NotificationService:
    def send_notification(self, message: str):
        """Send notification."""
        print(f"Notification sent: {message}")
        return True

@Injectable
class ReportService:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service
    
    @Cron(expression=CronExpression.EVERY_WEEKDAY)
    def generate_daily_report(self):
        """Generate and notify daily report."""
        # Generate report logic
        report = "Daily report generated successfully"
        
        # Send notification using injected service
        self.notification_service.send_notification(report)
        return report
```

## Creating a Complete Application

Here's how to create a complete PyNest application with scheduled tasks:

### Module Setup

```python
# task_module.py
from nest.core import Module
from .task_service import TaskService
from .notification_service import NotificationService

@Module(
    providers=[TaskService, NotificationService],
    exports=[TaskService],
)
class TaskModule:
    pass
```

### Application Module

```python
# app_module.py
from nest.core import Module, PyNestFactory
from .task_module import TaskModule

@Module(
    imports=[TaskModule],
)
class AppModule:
    pass

app = PyNestFactory.create(AppModule, title="Scheduler App", version="1.0.0")
```

### Running the Application

```python
# main.py
import uvicorn
from app_module import app

if __name__ == "__main__":
    uvicorn.run("app_module:app", host="0.0.0.0", port=8000, reload=True)
```

## Configuration

Task scheduling is automatically configured when you use the decorators. The scheduler starts automatically with your PyNest application and terminates gracefully on shutdown.

### Required Dependencies

Ensure the following dependencies are installed:

```bash
pip install APScheduler==3.10.4 pytz==2024.2 six==1.16.0 tzlocal==5.2
```

## Best Practices

1. **Use Predefined Expressions**: Leverage PyNest's predefined cron expressions for reliability.

2. **Handle Exceptions**: Always implement proper error handling in scheduled methods.

3. **Keep Tasks Lightweight**: Scheduled tasks should be quick to execute and non-blocking.

4. **Use Logging**: Implement comprehensive logging for monitoring and debugging.

5. **Test Thoroughly**: Test scheduled tasks in development before deploying to production.

## Troubleshooting

### Common Issues

**Tasks Not Running:**
- Verify the PyNest application is running
- Check that services are properly registered in modules
- Ensure scheduled methods have the correct signature

**Multiple Executions:**
- Avoid running multiple application instances
- Check for application restart loops
- Verify job ID generation is working correctly

## Conclusion 🎉

PyNest's task scheduling system provides a powerful and intuitive way to automate tasks in your applications. By leveraging the `@Cron` and `@Interval` decorators along with PyNest's dependency injection system, you can create robust scheduled tasks that integrate seamlessly with your application architecture.

The automatic detection and scheduling of decorated methods eliminates the need for manual configuration, making it easy to implement complex scheduling scenarios while maintaining clean, maintainable code.

---

<nav class="md-footer-nav">
  <a href="/PyNest/dependency_injection" class="md-footer-nav__link">
    <span>&larr; Dependency Injection</span>
  </a>
  <a href="/PyNest/mongodb" class="md-footer-nav__link">
    <span>MongoDB Integration &rarr;</span>
  </a>
</nav>