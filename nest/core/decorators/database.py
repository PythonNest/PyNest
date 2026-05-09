import logging
import time

from fastapi.exceptions import HTTPException

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def db_request_handler(func):
    """
    Decorator that wraps ORM service methods with timing, logging, and HTTP error
    conversion.  Session lifecycle (open / commit / rollback / close) is the
    responsibility of each service method — use config.get_session() there.
    """

    def wrapper(self, *args, **kwargs):
        try:
            start = time.time()
            result = func(self, *args, **kwargs)
            logger.info(f"db request finished in {time.time() - start:.3f}s")
            return result
        except HTTPException:
            raise  # already an HTTP error — let FastAPI handle it
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper


def async_db_request_handler(func):
    """
    Async version of db_request_handler.  Session lifecycle is the caller's
    responsibility (pass session via Depends or use config.get_session()).
    """

    async def wrapper(*args, **kwargs):
        try:
            start = time.time()
            result = await func(*args, **kwargs)
            logger.info(f"async db request finished in {time.time() - start:.3f}s")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper
