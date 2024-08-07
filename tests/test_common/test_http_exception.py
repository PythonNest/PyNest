import pytest
from nest.common.exceptions import NotFoundException, BadRequestException  
def test_not_found_exception_initialization():
    message = "Resource not found"
    exception = NotFoundException(message)
    
    assert exception.status == 404
    assert exception.message == message
    assert exception.get_status() == 404
    assert exception.get_response() == message


def test_not_found_exception_with_options():
    message = "Resource not found"
    options = {"cause": "Database error"}
    exception = NotFoundException(message, options)
    
    assert exception.status == 404
    assert exception.message == message
    assert exception.cause == "Database error"

def test_bad_request_exception_initialization():
    message = "Invalid input"
    exception = BadRequestException(message)
    
    assert exception.status == 400
    assert exception.message == message
    assert exception.get_status() == 400
    assert exception.get_response() == message

def test_bad_request_exception_create_body():
    message = "Invalid input"
    error = "ValidationError"
    status_code = 400
    body = BadRequestException.create_body(message, error, status_code)
    
    assert body == {
        "message": message,
        "error": error,
        "status_code": status_code
    }

def test_exceptions_inheritance():
    assert issubclass(NotFoundException, Exception)
    assert issubclass(BadRequestException, Exception)

@pytest.mark.parametrize("ExceptionClass", [NotFoundException, BadRequestException])
def test_exception_with_cause(ExceptionClass):
    cause = ValueError("Original error")
    exception = ExceptionClass("Error occurred", options={"cause": cause})
    
    assert exception.cause == cause