class CircularDependencyException(Exception):
    """Raised when a circular dependency is detected in the provider graph at build time."""

    def __init__(self, message: str = "Circular dependency detected"):
        super().__init__(message)


class UnknownModuleException(Exception):
    """Raised when a module cannot be found in the container."""
    pass


class NoneInjectableException(Exception):
    """Raised when a class without @Injectable is listed as a provider."""

    def __init__(self, message: str = "Non-injectable class detected"):
        super().__init__(message)
