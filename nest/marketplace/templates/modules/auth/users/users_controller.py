from nest.core import Depends, Controller, Post
from nest.marketplace.templates.modules.auth import UsersService
from src.users.users_model import User, UserLogin


@Controller("users")
class UsersController:
    service: UsersService = Depends(UsersService)

    @Post("register")
    def register(self, user: User):
        return self.service.register(user)

    @Post("login")
    def login(self, user_login: UserLogin):
        return self.service.login(user_login)

