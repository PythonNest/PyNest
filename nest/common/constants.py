from enum import Enum


class ModuleMetadata(Enum):
    CONTROLLERS = "controllers"
    IMPORT = "imports"
    PROVIDER = "providers"


INJECTABLE_TOKEN = "__injectable__"
