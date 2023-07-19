from nest.core import Controller, Get, Post, Depends

from examples.nest_products_mongo.src.users.users_service import UsersService
from examples.nest_products_mongo.src.users.users_model import User


@Controller("users")
class UsersController:

    users_service: UsersService = Depends(UsersService)

    @Get(path="/get_users")
    def get_users(self):
        return self.users_service.get_users()

    @Get("/get_user/{user_id}")
    def get_user(self, user_id: int):
        return self.users_service.get_user(user_id)

    @Post("/add_user")
    def add_users(self, user: User):
        return self.users_service.add_user(user)
