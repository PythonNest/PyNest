import pytest
from fastapi.responses import JSONResponse

from nest.common.exceptions import ExceptionFilter, ArgumentsHost, HttpException, NotFoundException
from nest.core.decorators.filters import Catch, UseFilters


# --- @Catch tests ---

def test_catch_stores_exception_types():
    @Catch(HttpException)
    class MyFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    assert MyFilter.__caught_exceptions__ == (HttpException,)


def test_catch_multiple_types():
    @Catch(ValueError, TypeError)
    class MyFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    assert MyFilter.__caught_exceptions__ == (ValueError, TypeError)


def test_catch_no_args_catches_all():
    @Catch()
    class CatchAllFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    assert CatchAllFilter.__caught_exceptions__ == ()


def test_catch_returns_the_class():
    @Catch(HttpException)
    class MyFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    assert issubclass(MyFilter, ExceptionFilter)


# --- @UseFilters on methods ---

def test_use_filters_on_method():
    @Catch(HttpException)
    class MyFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    def my_handler():
        pass

    decorated = UseFilters(MyFilter)(my_handler)
    assert MyFilter in decorated.__filters__


def test_use_filters_with_instance():
    @Catch(HttpException)
    class MyFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    def my_handler():
        pass

    instance = MyFilter()
    decorated = UseFilters(instance)(my_handler)
    assert instance in decorated.__filters__


def test_use_filters_multiple_on_method():
    @Catch(HttpException)
    class FilterA(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    @Catch(ValueError)
    class FilterB(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    def my_handler():
        pass

    decorated = UseFilters(FilterA, FilterB)(my_handler)
    assert FilterA in decorated.__filters__
    assert FilterB in decorated.__filters__


def test_use_filters_on_class():
    @Catch(HttpException)
    class MyFilter(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    @UseFilters(MyFilter)
    class MyController:
        pass

    assert MyFilter in MyController.__filters__


def test_use_filters_preserves_existing_filters():
    @Catch(HttpException)
    class FilterA(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    @Catch(ValueError)
    class FilterB(ExceptionFilter):
        async def catch(self, exception, host):
            return JSONResponse(status_code=500, content={})

    def my_handler():
        pass

    UseFilters(FilterA)(my_handler)
    UseFilters(FilterB)(my_handler)
    assert FilterA in my_handler.__filters__
    assert FilterB in my_handler.__filters__
