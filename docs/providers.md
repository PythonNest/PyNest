# Providers and Injectables in PyNest 🏗️

Providers, also known as services or injectables, are fundamental in PyNest applications. They handle business logic and other functionalities, acting as dependencies that can be injected into other components like controllers. This guide explains what providers are, how to use them, how to import and export them in modules, and how to inject them into controllers and other services, with various examples.

## What is a Provider?

In PyNest, a provider is a class annotated with the `@Injectable` decorator. This decorator makes the class available for dependency injection, allowing it to be injected into other classes such as controllers and services.

## Defining a Provider

To define a provider, use the `@Injectable` decorator. This makes the class available for dependency injection within the module or globally if exported.

**Example: Logger Service**

`logger_service.py`

```python
from nest.core import Injectable

@Injectable
class LoggerService:
    def log(self, message: str):
        print(f"LOG: {message}")
```

In this example, the `LoggerService` class is defined as a provider by using the `@Injectable` decorator. This class can now be injected into other classes within the same module or exported to be used in other modules.

## Using Providers in Modules

[Modules](modules.md) are used to group related providers, controllers, and other modules.
Providers can be imported and exported in modules to be used across the application.

**Example: S3 Module**
`s3_module.py`

```python
from nest.core import Module
from .s3_service import S3Service
from src.providers.logger.logger_service import LoggerService
from src.providers.logger.logger_module import LoggerModule


@Module(
    providers=[S3Service, LoggerService],
    exports=[S3Service],
    imports=[LoggerModule],
)
class S3Module:
    pass
```

In this example:

The S3Module defines a module that provides the S3Service and exports it for use in other modules.
It is also importing the LoggerModule to use the LoggerService.

## Injecting Providers into Controllers and Services

Providers can be injected into controllers and other services using dependency injection. This is done by declaring the dependency in the constructor of the class where the provider is needed.

**Example: S3 Service and Controller**

`s3_service.py`

```python
from nest.core import Injectable
from src.providers.logger.logger_service import LoggerService

@Injectable
class S3Service:
    
    def __init__(self, logger_service: LoggerService):
        self.logger_service = logger_service
    
    def upload_file(self, file_name: str):
        print(f"Uploading {file_name}")
        self.logger_service.log(f"Uploaded file: {file_name}")
```

In this Service, the `LoggerService` is injected into the `S3Service` via the constructor.

`s3_controller.py`

```python
from nest.core import Controller, Post
from .s3_service import S3Service

@Controller('/s3')
class S3Controller:
    def __init__(self, s3_service: S3Service):
        self.s3_service = s3_service

    @Post('/upload')
    def upload_file(self, file_name: str):
        self.s3_service.upload_file(file_name)
        return {"message": "File uploaded successfully!"}
```

In these examples:

The S3Service is injected into the S3Controller via the constructor.

## Importing and Exporting Providers
Providers can be shared between modules by importing and exporting them.

**Example: Email Module**

`email_module.py`

```python
from nest.core import Module
from src.providers.s3.s3_module import S3Module
from src.providers.s3.s3_service import S3Service
from .email_service import EmailService

@Module(
    imports=[S3Module],
    providers=[EmailService, S3Service],
    exports=[EmailService],
)
class EmailModule:
    pass
```

In this example:

The EmailModule imports the S3Module to use the S3Service provided by it.

The EmailService is defined as a provider in the EmailModule and exported for use in other modules.

## Conclusion

Providers are essential components in PyNest applications, handling business logic and other functionalities.
By defining, importing, exporting,
and injecting providers, you can create modular and maintainable applications with clear separation of concerns.
Understanding how providers work and how to use them effectively will help
you build robust and scalable applications with PyNest.

---

<nav class="md-footer-nav">
  <a href="/PyNest/controllers" class="md-footer-nav__link">
    <span>&larr; Controllers</span>
  </a>
  <a href="/PyNest/dependency_injection" class="md-footer-nav__link">
    <span>Dependency Injection &rarr;</span>
  </a>
</nav>