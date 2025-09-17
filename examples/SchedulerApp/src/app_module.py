from .app_controller import AppController
from .app_service import AppService
from .scheduler_service import SchedulerService

from nest.core import Module, PyNestFactory

@Module(
    controllers=[AppController],
    providers=[AppService, SchedulerService],
)
class AppModule:
    pass

app = PyNestFactory.create(
    AppModule,
    description="PyNest Application with Task Scheduling",
    title="Scheduler App",
    version="1.0.0",
    debug=True
)

http_server = app.get_server()