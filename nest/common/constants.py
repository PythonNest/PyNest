from enum import Enum


class ModuleMetadata(str, Enum):
    CONTROLLERS = "controllers"
    IMPORTS = "imports"
    PROVIDERS = "providers"
    EXPORTS = "exports"

    def __str__(self):
        return self.value


INJECTABLE_TOKEN = "__injectable__"
INJECTABLE_NAME = "__injectable__name__"
STATUS_CODE_TOKEN = "status_code"
DEPENDENCIES = "__dependencies__"
