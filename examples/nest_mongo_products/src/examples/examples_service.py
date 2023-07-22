from src.examples.examples_model import Examples
from src.examples.examples_entity import Examples as ExamplesEntity
from nest.core.decorators import db_request_handler
from functools import lru_cache


@lru_cache()
class ExamplesService:

    @db_request_handler
    async def add_examples(self, examples: Examples):
        new_examples = ExamplesEntity(
            **examples.dict()
        )
        await new_examples.save()
        return new_examples.id

    @db_request_handler
    async def get_examples(self):
        return await ExamplesEntity.find_all().to_list()

