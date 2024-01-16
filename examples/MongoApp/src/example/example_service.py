from .example_model import Example
from .example_entity import Example as ExampleEntity
from nest.core.decorators import db_request_handler
from functools import lru_cache


@lru_cache()
class ExampleService:
    @db_request_handler
    async def add_example(self, example: Example):
        new_example = ExampleEntity(**example.dict())
        await new_example.save()
        return new_example.id

    @db_request_handler
    async def get_example(self):
        return await ExampleEntity.find_all().to_list()
