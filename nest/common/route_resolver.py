from nest.engine.proto import App, Router


class RoutesResolver:
    def __init__(self, container, app_ref: App):
        self.container = container
        self.app_ref = app_ref

    def register_routes(self):
        for module in self.container.modules.values():
            for controller in module.controllers.values():
                self.register_route(controller)

    def register_route(self, controller):
        router: Router = controller.get_router()
        self.app_ref.include_router(router)

