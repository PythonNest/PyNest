from .example_model import Example
from nest.core.decorators import Injectable
import time
from functools import lru_cache


@lru_cache()
class ExampleService:
    def __init__(self):
        self.database = []
        time.sleep(5)

    def get_example(self):
        return self.database

    def add_example(self, example: Example):
        self.database.append(example)
        return example
