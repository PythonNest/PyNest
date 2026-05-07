from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import Request


class CircularDependencyException(Exception):
    def __init__(self, message="Circular dependency detected"):
        super().__init__(message)


class UnknownModuleException(Exception):
    pass


class NoneInjectableException(Exception):
    def __init__(self, message="None Injectable Classe Detected"):
        super().__init__(message)


class HttpException(Exception):
    def __init__(self, message: str = "Internal Server Error", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BadRequestException(HttpException):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message=message, status_code=400)


class UnauthorizedException(HttpException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(HttpException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403)


class NotFoundException(HttpException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message=message, status_code=404)


class MethodNotAllowedException(HttpException):
    def __init__(self, message: str = "Method Not Allowed"):
        super().__init__(message=message, status_code=405)


class ConflictException(HttpException):
    def __init__(self, message: str = "Conflict"):
        super().__init__(message=message, status_code=409)


class UnprocessableEntityException(HttpException):
    def __init__(self, message: str = "Unprocessable Entity"):
        super().__init__(message=message, status_code=422)


class InternalServerErrorException(HttpException):
    def __init__(self, message: str = "Internal Server Error"):
        super().__init__(message=message, status_code=500)


class HttpArgumentsHost:
    def __init__(self, request: Optional["Request"]):
        self._request = request

    def get_request(self) -> Optional["Request"]:
        return self._request

    def get_response(self):
        return None


class ArgumentsHost:
    def __init__(self, request: Optional["Request"]):
        self._request = request

    def switch_to_http(self) -> HttpArgumentsHost:
        return HttpArgumentsHost(self._request)

    def get_type(self) -> str:
        return "http"


class ExceptionFilter(ABC):
    @abstractmethod
    async def catch(self, exception: Exception, host: "ArgumentsHost"):
        ...
