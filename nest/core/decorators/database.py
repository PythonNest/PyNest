from fastapi.exceptions import HTTPException
import logging
import time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
            s = time.time()
            result = func(self, *args, **kwargs)
            p_time = time.time() - s
            logging.info(f"request finished after {p_time}")
            self.session.close()
            return result
        except Exception as e:
            logging.error(e)
            self.session.rollback()
            self.session.close()
            return HTTPException(status_code=500, detail=str(e))

    return wrapper
