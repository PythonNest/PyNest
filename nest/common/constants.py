from enum import Enum


class ModuleMetadata(Enum):
    CONTROLLERS = "controllers"
    IMPORT = "imports"
    PROVIDER = "providers"


INJECTABLE_TOKEN = "__injectable__"
STATUS_CODE_TOKEN = "status_code"
