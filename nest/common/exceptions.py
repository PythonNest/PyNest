class CircularDependencyException(Exception):
    def __init__(self, message="Circular dependency detected"):
        super().__init__(message)


class UnknownModuleException(Exception):
    pass


class NoneInjectableException(Exception):
    def __init__(self, message="None Injectable Classe Detected"):
        super().__init__(message)
