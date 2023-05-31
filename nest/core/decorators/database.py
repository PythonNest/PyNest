from fastapi.exceptions import HTTPException


def db_request_handler(func):
    """
    Decorator that handles database requests, including error handling and session management.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
            self.session.close()
            return result
        except Exception as e:
            self.session.rollback()
            self.session.close()
            return HTTPException(status_code=500, detail=str(e))

    return wrapper
