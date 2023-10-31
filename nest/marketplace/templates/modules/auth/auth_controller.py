AUTH_CONTROLLER_TEMPLATE = """from nest.core import Depends, Controller, Post
from src.auth.auth_service import AuthService
from src.auth.auth_model import User, UserLogin


@Controller("auth")
class AuthController:
    service: UsersService = Depends(AuthService)

    @Post("register")
    def register(self, user: User):
        return self.service.register(user)

    @Post("login")
    def login(self, user_login: UserLogin):
        return self.service.login(user_login)

"""


