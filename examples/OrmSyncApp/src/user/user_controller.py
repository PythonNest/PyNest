from nest.core import Controller, Get, Post, Depends
from .user_service import UserService
from .user_model import User


@Controller("user")
class UserController:

    service: UserService = Depends(UserService)

    @Get("/")
    def get_users(self):
        return self.service.get_users()

    @Post("/")
    def add_user(self, user: User):
        return self.service.add_user(user)
