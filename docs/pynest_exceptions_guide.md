# Pynest Exceptions Guide

This guide provides a comprehensive overview of the exception handling system in Pynest, including built-in exceptions, custom exception creation, and best practices for integrating exceptions into your services and controllers.

## Table of Contents

1. [Introduction](#introduction)
2. [Available Exception Types](#available-exception-types)
3. [Creating Custom Exceptions](#creating-custom-exceptions)
4. [Using Exceptions in Services](#using-exceptions-in-services)
5. [Using Exceptions in Controllers](#using-exceptions-in-controllers)
6. [Best Practices](#best-practices)

## Introduction

Exception handling is a critical aspect of any robust and maintainable application. Pynest provides a set of built-in exceptions to handle common HTTP errors, as well as the ability to create custom exceptions tailored to your application's specific needs. By understanding and using these exceptions effectively, you can ensure consistent error handling and improve the user experience in your application.

## Available Exception Types

Pynest offers a range of built-in HTTP exceptions, all of which extend from the base `HttpException` class. These exceptions are designed to correspond to common HTTP status codes, allowing you to easily manage error responses in a standardized way.

### Built-In HTTP Exceptions

- **`BadRequestException` (400)**: Indicates that the server cannot process the request due to client-side input errors.
- **`UnauthorizedException` (401)**: Indicates that the client must authenticate itself to get the requested response.
- **`ForbiddenException` (403)**: Indicates that the client does not have permission to access the requested resource.
- **`NotFoundException` (404)**: Indicates that the server cannot find the requested resource.
- **`MethodNotAllowedException` (405)**: Indicates that the request method is not supported for the requested resource.
- **`NotAcceptableException` (406)**: Indicates that the requested resource is capable of generating only content not acceptable according to the Accept headers sent in the request.
- **`RequestTimeoutException` (408)**: Indicates that the server timed out waiting for the request.
- **`ConflictException` (409)**: Indicates that the request could not be processed because of conflict in the current state of the resource.
- **`GoneException` (410)**: Indicates that the requested resource is no longer available and will not be available again.
- **`PayloadTooLargeException` (413)**: Indicates that the request entity is larger than the server is willing or able to process.
- **`UnsupportedMediaTypeException` (415)**: Indicates that the media format of the requested data is not supported by the server.
- **`UnprocessableEntityException` (422)**: Indicates that the server understands the content type of the request entity, but was unable to process the contained instructions.
- **`TooManyRequestsException` (429)**: Indicates that the user has sent too many requests in a given amount of time ("rate limiting").
- **`InternalServerErrorException` (500)**: Indicates that the server encountered an unexpected condition that prevented it from fulfilling the request.
- **`ServiceUnavailableException` (503)**: Indicates that the server is not ready to handle the request, typically due to temporary overloading or maintenance.

## Creating Custom Exceptions

In addition to the built-in exceptions, Pynest allows you to define custom exceptions to handle specific application-level errors. Custom exceptions should extend the `HttpException` class or a relevant subclass to ensure they integrate seamlessly with Pynest's error-handling system.

### Example: Creating a Custom Exception

```python
from pynest.exception import HttpException

class CustomException(HttpException):
    def __init__(self, message: str):
        super().__init__(message, 418)  # 418 is an example status code
```

In this example, `CustomException` is created with a specific message and an HTTP status code of 418. You can now throw this exception from your services or controllers.

## Using Exceptions in Services

Exceptions play a vital role in service logic, particularly when handling scenarios like validation errors, resource not found errors, or any business logic that needs to notify the client about an issue.

### Example: Using Exceptions in a Service

```python
from pynest.exception import BadRequestException, NotFoundException
from pynest.decorators import Injectable
from .user_model import User

@Injectable
class UserService:
    def __init__(self):
        self.users: List[User] = []  # Mock database as a list

    def get_user(self, user_id: int) -> User:
        user = next((user for user in self.users if user.id == user_id), None)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return user

    def create_user(self, user_data: dict) -> User:
        if 'name' not in user_data:
            raise BadRequestException("Name is required")
        new_user = User(id=len(self.users) + 1, name=user_data['name'])
        self.users.append(new_user)
        return new_user
```

In this service example:
- `NotFoundException` is thrown if a user is not found in the list.
- `BadRequestException` is used to handle cases where required user data is missing.

## Using Exceptions in Controllers

Controllers are responsible for handling incoming requests and sending responses to the client. When exceptions occur in services, they can be caught and managed within controllers, ensuring that appropriate HTTP responses are sent back to the client.

### Example: Using Exceptions in a Controller

```python
from pynest.controller import Controller, Get, Post, Param, Body
from pynest.exception import BadRequestException, InternalServerErrorException
from .user_service import UserService

@Controller('users')
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @Get(':id')
    def get_user(self, @Param('id') user_id: int):
        try:
            return self.user_service.get_user(user_id)
        except NotFoundException as e:
            raise e  # Re-throw to be handled globally or return specific response
        except Exception as e:
            raise InternalServerErrorException(f"An error occurred: {str(e)}")

    @Post()
    def create_user(self, @Body() user_data: dict):
        try:
            return self.user_service.create_user(user_data)
        except BadRequestException as e:
            raise e  # Specific exception for bad request
        except Exception as e:
            raise InternalServerErrorException(f"An error occurred: {str(e)}")
```

In this controller example:
- Specific exceptions like `NotFoundException` and `BadRequestException` are handled explicitly.
- General exceptions are wrapped in an `InternalServerErrorException` to ensure that unexpected errors do not expose sensitive information.

## Best Practices

1. **Use Specific Exceptions**: Use the most specific exception type that accurately reflects the error scenario. This helps in providing clear and precise feedback to the client.

2. **Create Custom Exceptions for Domain-Specific Errors**: When your application logic requires error handling that isn't covered by the built-in exceptions, create custom exceptions to encapsulate these scenarios.

3. **Avoid Exposing Sensitive Information**: Ensure that exception messages do not expose sensitive information, especially in production environments. Use generic messages or codes where necessary.

4. **Log All Exceptions in Production**: Logging is crucial for debugging and monitoring. Ensure that all exceptions, particularly unhandled ones, are logged with sufficient detail to trace issues.

5. **Validate Early**: Perform input validation as early as possible, using `BadRequestException` or custom validation exceptions. This prevents the application from processing invalid data.

6. **Gracefully Handle Known Edge Cases**: Anticipate potential edge cases (like missing resources or invalid operations) and handle them gracefully using appropriate exceptions (`NotFoundException`, `ConflictException`, etc.).

By following these best practices and fully utilizing Pynest's exception system, you can build applications that are not only robust and maintainable but also provide a seamless and user-friendly experience.

--- 