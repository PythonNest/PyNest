from nest.common.constants import ModuleMetadata


class Module:
    def __init__(self, imports=None, controllers=None, providers=None):
        self.controllers = controllers or []
        self.providers = providers or []
        self.imports = imports or []

    def __call__(self, cls):
        setattr(cls, ModuleMetadata.CONTROLLERS.value, self.controllers)
        setattr(cls, ModuleMetadata.PROVIDER.value, self.providers)
        setattr(cls, ModuleMetadata.IMPORT.value, self.imports)

        return cls
