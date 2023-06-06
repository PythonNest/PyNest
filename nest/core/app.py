from typing import List, Callable
from fastapi import FastAPI, APIRouter


class App(FastAPI):
    def __init__(self, description: str, modules: List, init_db: Callable = None):
        """
        Initializes the App instance.

        Args:
            description (str): The description of the application.
            modules (List): A list of modules to register.
            init_db (Callable, optional): A callable function to initialize the database. Defaults to None.

        """
        super().__init__(description=description)
        self.modules = modules
        self._register_controllers()
        if init_db:
            init_db()

    def _register_controllers(self):
        """
        Registers the controllers from the provided modules.

        """
        for module in self.modules:
            module_instance = module()
            for controller in module_instance.controllers:
                router: APIRouter = controller.get_router()
                self.include_router(router)
