from nest.core import Injectable
from nest.core.decorators.database import db_request_handler

from .example_entity import Example as ExampleEntity
from .example_model import Example

import asyncio


@Injectable
class ExampleService:

    @db_request_handler
    async def add_example(self, example: Example):
        new_example = ExampleEntity(**example.dict())
        await new_example.save()
        return new_example.id

    @db_request_handler
    async def get_example(self):
        await asyncio.sleep(5)
        return await ExampleEntity.find_all().to_list()
