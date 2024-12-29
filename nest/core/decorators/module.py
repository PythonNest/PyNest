from nest.common.constants import ModuleMetadata
from typing import List
import dataclasses


@dataclasses.dataclass(frozen=True)
class Module:
    controllers: List[type] = dataclasses.field(default_factory=list)
    providers: List[type] = dataclasses.field(default_factory=list)
    exports: List[type] = dataclasses.field(default_factory=list)
    imports: List[type] = dataclasses.field(default_factory=list)
    is_global: bool = dataclasses.field(default=False)

    def __call__(self, cls):
        setattr(cls, ModuleMetadata.CONTROLLERS, self.controllers)
        setattr(cls, ModuleMetadata.PROVIDERS, self.providers)
        setattr(cls, ModuleMetadata.IMPORTS, self.imports)
        setattr(cls, ModuleMetadata.EXPORTS, self.exports)
        setattr(cls, "__is_module__", True)
        setattr(cls, "__is_global__", self.is_global)

        return cls
