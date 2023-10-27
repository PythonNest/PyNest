from nest.core.decorators import Module 
from app_controller import AppController
from app_service import AppService
from src.products.products_module import ProductModule 
from src.users.users_module import UserModule
from src.test.test_module import TestModule

@Module(
  imports=[
    ProductModule, 
    UserModule,
    TestModule, 
  ],
  providers=[AppService],
  controllers=[AppController]
)
class AppModule: 
     pass 