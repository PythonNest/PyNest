import logging
import time

from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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
            if hasattr(self, "session"):
                # Check if self is an instance of OrmService
                self.session.close()
            return result
        except Exception as e:
            logging.error(e)
            if hasattr(self, "session"):
                # Check if self is an instance of OrmService
                self.session.rollback()
                self.session.close()
            return HTTPException(status_code=500, detail=str(e))

    return wrapper


def async_db_request_handler(func):
    """
    Asynchronous decorator that handles database requests, including error handling,
    session management, and logging for async functions.

    Args:
        func (function): The async function to be decorated.

    Returns:
        function: The decorated async function.
    """

    async def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)  # Awaiting the async function
            process_time = time.time() - start_time
            logger.info(f"Async request finished after {process_time} seconds")
            return result
        except Exception as e:
            self = args[0] if args else None
            session = getattr(self, "session", None)
            # If not found, check in function arguments
            if session:
                session_type = "class"
            else:
                session = [arg for arg in args if isinstance(arg, AsyncSession)][0]
                if session:
                    session_type = "function"
                else:
                    raise ValueError("AsyncSession not provided to the function")

            logger.error(f"Error in async request: {e}")
            # Rollback if session is in a transaction
            if session and session_type == "function" and session.in_transaction():
                await session.rollback()
            elif session and session_type == "class":
                async with session() as session:
                    await session.rollback()
            return HTTPException(status_code=500, detail=str(e))

    return wrapper
