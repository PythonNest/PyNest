from nest.core.decorators import Injectable

from ..user.user_service import UserService
from .example_model import Example


@Injectable
class ExampleService:
    def __init__(self, user_service: UserService):
        self.database = []
        self.user_service = user_service

    def get_example(self):
        return self.database

    def add_example(self, example: Example):
        self.database.append(example)
        return example
