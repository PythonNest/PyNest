from typing import Type


def Catch(*exception_types: Type[Exception]):
    """Bind an ExceptionFilter class to one or more exception types.

    Usage::

        @Catch(HttpException)
        class MyFilter(ExceptionFilter):
            async def catch(self, exception, host):
                ...

    An empty ``@Catch()`` means the filter catches every exception.
    """
    def decorator(cls):
        cls.__caught_exceptions__ = tuple(exception_types)
        return cls

    return decorator


def UseFilters(*filters):
    """Apply exception filters to a controller class or a route method.

    Filters are tried in declaration order.  Pass filter classes *or*
    pre-instantiated filter objects.

    Usage::

        @Controller('/users')
        @UseFilters(HttpExceptionFilter)          # class-level
        class UserController:
            @Get('/:id')
            @UseFilters(NotFoundFilter())          # method-level instance
            def get_user(self, id: int): ...
    """
    def decorator(obj):
        existing = list(getattr(obj, '__filters__', []))
        existing.extend(filters)
        obj.__filters__ = existing
        return obj

    return decorator
