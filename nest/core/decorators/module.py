from nest.common.constants import ModuleMetadata


class Module:
    def __init__(
        self,
        imports=None,
        controllers=None,
        providers=None,
        exports=None,
        is_global: bool = False,
    ):
        self.controllers = controllers or []
        self.providers = providers or []
        self.imports = imports or []
        self.exports = exports
        self.is_global = is_global

    def __call__(self, cls):
        setattr(cls, ModuleMetadata.CONTROLLERS, self.controllers)
        setattr(cls, ModuleMetadata.PROVIDERS, self.providers)
        setattr(cls, ModuleMetadata.IMPORTS, self.imports)
        setattr(cls, ModuleMetadata.EXPORTS, self.exports)
        setattr(cls, "__is_module__", True)
        setattr(cls, "__is_global__", self.is_global)

        return cls
