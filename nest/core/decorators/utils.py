from nest.common.constants import STATUS_CODE_TOKEN


def HttpCode(status_code: int):
    """
    Decorator that sets the HTTP status code for a route.

    Args:
        status_code (int): The HTTP status code for the response.
    """

    def decorator(func):
        if not hasattr(func, STATUS_CODE_TOKEN):
            setattr(func, STATUS_CODE_TOKEN, status_code)
        return func

    return decorator
