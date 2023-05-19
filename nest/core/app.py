from typing import List, Callable
from fastapi import FastAPI, APIRouter


class App(FastAPI):

    def __init__(self, description: str, modules: List, init_db: Callable = None):
        super().__init__(description=description)
        self.modules = modules
        self._register_controllers()
        if init_db:
            init_db()

    def _register_controllers(self):
        for module in self.modules:
            module_instance = module()
            for controller in module_instance.controllers:
                router: APIRouter = controller.get_router()
                self.include_router(router)
