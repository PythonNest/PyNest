from nest import __version__
from nest.core import Injectable


@Injectable
class AppService:
    def __init__(self):
        self.app_name = "PyNest CLI App"
        self.app_version = __version__

    def get_app_info(self):
        return {"app_name": self.app_name, "app_version": self.app_version}
