from nest.core import Controller, Get

from .app_service import AppService


@Controller("/")
class AppController:
    def __init__(self, service: AppService):
        self.service = service

    @Get("/")
    async def get_app_info(self):
        return await self.service.get_app_info()
