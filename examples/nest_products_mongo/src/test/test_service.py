from examples.nest_products_mongo.src.test.test_model import Test
from examples.nest_products_mongo.src.test.test_entity import Test as TestEntity
from nest.core.decorators import db_request_handler


class TestService:

    @db_request_handler
    def add_test(self, test: Test):
        new_test = TestEntity(**test.dict())
        new_test.save()
        return new_test.id

    @db_request_handler
    def get_test(self):
        return TestEntity.find_all()
