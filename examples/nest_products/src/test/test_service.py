from examples.nest_products.src.test.test_model import Test
from examples.nest_products.src.test.test_entity import Test as TestEntity
from examples.nest_products.orm_config import config
from nest.core.decorators import db_request_handler


class TestService:
    def __init__(self):
        self.orm_config = config
        self.session = self.orm_config.get_db()

    @db_request_handler
    def add_test(self, test: Test):
        new_test = TestEntity(**test.dict())
        self.session.add(new_test)
        self.session.commit()
        return new_test.id

    @db_request_handler
    def get_test(self):
        return self.session.query(TestEntity).all()
