
def Get(path: str, **kwargs):
    """
    Decorator that defines a GET route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "GET"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Post(path: str, **kwargs):
    """
    Decorator that defines a POST route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "POST"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Delete(path: str, **kwargs):
    """
    Decorator that defines a DELETE route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "DELETE"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Put(path: str, **kwargs):
    """
    Decorator that defines a PUT route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "PUT"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator


def Patch(path: str, **kwargs):
    """
    Decorator that defines a PATCH route for the controller.

    Args:
        path (str): The URL path for the route.
        **kwargs: Additional keyword arguments to configure the route.

    Returns:
        function: The decorated function.

    """

    def decorator(func):
        func.method = "PATCH"
        func.__path__ = path
        func.__kwargs__ = kwargs
        return func

    return decorator
