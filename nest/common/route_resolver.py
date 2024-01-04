from fastapi import FastAPI, APIRouter
from nest.core.pynest_container import PyNestContainer


class RoutesResolver:
    def __init__(self, container: PyNestContainer, app_ref: FastAPI):
        self.container = container
        self.app_ref = app_ref

    def register_routes(self):
        for module in self.container.modules.values():
            for controller in module.controllers.values():
                self.register_route(controller)
        else:
            pass

    def register_route(self, controller):
        router: APIRouter = controller.get_router()
        self.app_ref.include_router(router)
