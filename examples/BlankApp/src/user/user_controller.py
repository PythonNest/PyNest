from nest.core import Controller, Get, Post, Depends
from .user_service import UserService
from .user_model import User


@Controller("user")
class UserController:

    service: UserService = Depends(UserService)
    
    @Get("/")
    def get_user(self):
        return self.service.get_user()
        
    @Post("/")
    def add_user(self, user: User):
        return self.service.add_user(user)

