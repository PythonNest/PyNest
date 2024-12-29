from http import HTTPStatus
from typing import Any, Dict, Optional, Union  
class CircularDependencyException(Exception):
    def __init__(self, message="Circular dependency detected"):
        super().__init__(message)


class UnknownModuleException(Exception):
    pass


class NoneInjectableException(Exception):
    def __init__(self, message="None Injectable Classe Detected"):
        super().__init__(message)


class HttpException(Exception):
    """
    Defines the base HTTP exception, which can be handled by a custom exception handler.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], status: int, options: Optional[Dict[str, Any]] = None):
        """
        Instantiate a plain HTTP Exception.

        :param response: string, object describing the error condition or the error cause.
        :param status: HTTP response status code.
        :param options: An object used to add an error cause.
        """
        super().__init__()
        self.response = response
        self.status = status
        self.options = options or {}
        self.cause = self.options.get('cause')
        self.message = self.init_message()
        self.name = self.__class__.__name__

    def init_message(self) -> str:
        if isinstance(self.response, str):
            return self.response
        elif isinstance(self.response, dict) and 'message' in self.response and isinstance(self.response['message'], str):
            return self.response['message']
        else:
            return ' '.join([word for word in self.__class__.__name__.split('')]) or 'Error'

    def get_response(self) -> Union[str, Dict[str, Any]]:
        return self.response

    def get_status(self) -> int:
        return self.status

    @staticmethod
    def create_body(message: Optional[Union[str, Dict[str, Any]]] = None, error: Optional[str] = None, status_code: Optional[int] = None) -> Dict[str, Any]:
        if message is None:
            return {
                'message': error,
                'status_code': status_code,
            }

        if isinstance(message, (str, list)):
            return {
                'message': message,
                'error': error,
                'status_code': status_code,
            }

        return message

    @staticmethod
    def get_description_from(description_or_options: Union[str, Dict[str, Any]]) -> str:
        return description_or_options if isinstance(description_or_options, str) else description_or_options.get('description', '')

    @staticmethod
    def get_http_exception_options_from(description_or_options: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        return {} if isinstance(description_or_options, str) else description_or_options

    @staticmethod
    def extract_description_and_options_from(description_or_options: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        description = description_or_options if isinstance(description_or_options, str) else description_or_options.get('description', '')
        http_exception_options = {} if isinstance(description_or_options, str) else description_or_options
        return {
            'description': description,
            'http_exception_options': http_exception_options,
        }



class BadRequestException(HttpException):
    """
    Exception for 400 Bad Request errors.

    This exception should be raised when the server cannot or will not process
    the request due to an apparent client error.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new BadRequestException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.BAD_REQUEST, options=options)

class UnauthorizedException(HttpException):
    """
    Exception for 401 Unauthorized errors.

    This exception should be raised when authentication is required but has failed
    or has not been provided.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new UnauthorizedException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=401, options=options)

class ForbiddenException(HttpException):
    """
    Exception for 403 Forbidden errors.

    This exception should be raised when the server understands the request
    but refuses to authorize it.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new ForbiddenException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.FORBIDDEN, options=options)

class NotFoundException(HttpException):
    """
    Exception for 404 Not Found errors.

    This exception should be raised when the server cannot find the requested resource.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new NotFoundException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.NOT_FOUND, options=options)

class MethodNotAllowedException(HttpException):
    """
    Exception for 405 Method Not Allowed errors.

    This exception should be raised when the method specified in the request is
    not allowed for the resource identified by the request URI.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new MethodNotAllowedException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.METHOD_NOT_ALLOWED, options=options)

class NotAcceptableException(HttpException):
    """
    Exception for 406 Not Acceptable errors.

    This exception should be raised when the server cannot produce a response
    matching the list of acceptable values defined in the request's proactive
    content negotiation headers.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new NotAcceptableException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.NOT_ACCEPTABLE, options=options)

class RequestTimeoutException(HttpException):
    """
    Exception for 408 Request Timeout errors.

    This exception should be raised when the server timed out waiting for the request.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new RequestTimeoutException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.REQUEST_TIMEOUT, options=options)

class ConflictException(HttpException):
    """
    Exception for 409 Conflict errors.

    This exception should be raised when a request conflicts with the current
    state of the server.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new ConflictException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.CONFLICT, options=options)

class GoneException(HttpException):
    """
    Exception for 410 Gone errors.

    This exception should be raised when the requested resource is no longer
    available and will not be available again.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new GoneException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.GONE, options=options)

class PayloadTooLargeException(HttpException):
    """
    Exception for 413 Payload Too Large errors.

    This exception should be raised when the request entity is larger than
    limits defined by server.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new PayloadTooLargeException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE, options=options)

class UnsupportedMediaTypeException(HttpException):
    """
    Exception for 415 Unsupported Media Type errors.

    This exception should be raised when the media format of the requested data
    is not supported by the server.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new UnsupportedMediaTypeException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE, options=options)

class UnprocessableEntityException(HttpException):
    """
    Exception for 422 Unprocessable Entity errors.

    This exception should be raised when the server understands the content type
    of the request entity, and the syntax of the request entity is correct, but
    it was unable to process the contained instructions.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new UnprocessableEntityException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.UNPROCESSABLE_ENTITY, options=options)

class TooManyRequestsException(HttpException):
    """
    Exception for 429 Too Many Requests errors.

    This exception should be raised when the user has sent too many requests
    in a given amount of time ("rate limiting").

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new TooManyRequestsException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.TOO_MANY_REQUESTS, options=options)

class InternalServerErrorException(HttpException):
    """
    Exception for 500 Internal Server Error errors.

    This exception should be raised when the server encounters an unexpected
    condition that prevents it from fulfilling the request.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new InternalServerErrorException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.INTERNAL_SERVER_ERROR, options=options)

class ServiceUnavailableException(HttpException):
    """
    Exception for 503 Service Unavailable errors.

    This exception should be raised when the server is not ready to handle the request.
    Common causes are a server that is down for maintenance or that is overloaded.

    Attributes:
        Inherits all attributes from HttpException.
    """

    def __init__(self, response: Union[str, Dict[str, Any]], options: Optional[Dict[str, Any]] = None):
        """
        Initialize a new ServiceUnavailableException.

        Args:
            response (Union[str, Dict[str, Any]]): The error message or response body.
            options (Optional[Dict[str, Any]], optional): Additional options. Defaults to None.
        """
        super().__init__(response, status=HTTPStatus.SERVICE_UNAVAILABLE, options=options)