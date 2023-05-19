from nest.core import Controller, Get, Post, Depends

from examples.nest_products.src.test.test_service import TestService
from examples.nest_products.src.test.test_model import Test


@Controller("test")
class TestController:

    service: TestService = Depends(TestService)
    
    @Get("/get_test")
    def get_test(self):
        return self.service.get_test()
                
    @Post("/add_test")
    def add_test(self, test: Test):
        return self.service.add_test(test)
 