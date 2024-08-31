import pytest
from nest.common.exceptions import (
    CircularDependencyException, UnknownModuleException, NoneInjectableException,
    HttpException, BadRequestException, UnauthorizedException, ForbiddenException,
    NotFoundException, MethodNotAllowedException, NotAcceptableException,
    RequestTimeoutException, ConflictException, GoneException,
    PayloadTooLargeException, UnsupportedMediaTypeException,
    UnprocessableEntityException, TooManyRequestsException,
    InternalServerErrorException, ServiceUnavailableException
)

@pytest.mark.parametrize("ExceptionClass, status_code", [
    (BadRequestException, 400),
    (UnauthorizedException, 401),
    (ForbiddenException, 403),
    (NotFoundException, 404),
    (MethodNotAllowedException, 405),
    (NotAcceptableException, 406),
    (RequestTimeoutException, 408),
    (ConflictException, 409),
    (GoneException, 410),
    (PayloadTooLargeException, 413),
    (UnsupportedMediaTypeException, 415),
    (UnprocessableEntityException, 422),
    (TooManyRequestsException, 429),
    (InternalServerErrorException, 500),
    (ServiceUnavailableException, 503),
])
def test_http_exception_initialization(ExceptionClass, status_code):
    message = f"Test {ExceptionClass.__name__}"
    exception = ExceptionClass(message)
    
    assert exception.status == status_code
    assert exception.message == message
    assert exception.get_status() == status_code
    assert exception.get_response() == message

@pytest.mark.parametrize("ExceptionClass", [
    BadRequestException, UnauthorizedException, ForbiddenException,
    NotFoundException, MethodNotAllowedException, NotAcceptableException,
    RequestTimeoutException, ConflictException, GoneException,
    PayloadTooLargeException, UnsupportedMediaTypeException,
    UnprocessableEntityException, TooManyRequestsException,
    InternalServerErrorException, ServiceUnavailableException
])
def test_http_exception_with_options(ExceptionClass):
    message = f"Test {ExceptionClass.__name__}"
    options = {"cause": "Test cause"}
    exception = ExceptionClass(message, options)
    
    assert exception.message == message
    assert exception.cause == "Test cause"



def test_http_exception_create_body():
    message = "Test message"
    error = "TestError"
    status_code = 400
    body = HttpException.create_body(message, error, status_code)
    
    assert body == {
        "message": message,
        "error": error,
        "status_code": status_code
    }

def test_exceptions_inheritance():
    assert issubclass(CircularDependencyException, Exception)
    assert issubclass(UnknownModuleException, Exception)
    assert issubclass(NoneInjectableException, Exception)
    assert all(issubclass(exc, HttpException) for exc in [
        BadRequestException, UnauthorizedException, ForbiddenException,
        NotFoundException, MethodNotAllowedException, NotAcceptableException,
        RequestTimeoutException, ConflictException, GoneException,
        PayloadTooLargeException, UnsupportedMediaTypeException,
        UnprocessableEntityException, TooManyRequestsException,
        InternalServerErrorException, ServiceUnavailableException
    ])
    assert issubclass(HttpException, Exception)

@pytest.mark.parametrize("ExceptionClass", [
    BadRequestException, UnauthorizedException, ForbiddenException,
    NotFoundException, MethodNotAllowedException, NotAcceptableException,
    RequestTimeoutException, ConflictException, GoneException,
    PayloadTooLargeException, UnsupportedMediaTypeException,
    UnprocessableEntityException, TooManyRequestsException,
    InternalServerErrorException, ServiceUnavailableException
])
def test_exception_with_cause(ExceptionClass):
    cause = ValueError("Original error")
    exception = ExceptionClass("Error occurred", options={"cause": cause})
    
    assert exception.cause == cause 
    
