from typing import List
from fastapi import FastAPI, APIRouter


class App(FastAPI):
    def __init__(
            self,
            description: str,
            modules: List,
            title: str = "PyNest Service",
            **kwargs
    ):
        """
        Initializes the App instance.

        Args:
            description (str): The description of the application.
            modules (List): A list of modules to register.

        """
        super().__init__(
            description=description, title=title, **kwargs
        )
        self.modules = modules
        self._register_controllers()

    def _register_controllers(self):
        """
        Registers the controllers from the provided modules.
        """
        for module in self.modules:
            module_instance = module()
            for controller in module_instance.controllers:
                router: APIRouter = controller.get_router()
                self.include_router(router)
