from nest.core import Controller, Get, Post
from nest.core.protocols import Param, Query, Header, Body
import uuid
from .user_model import User
from .user_service import UserService


@Controller("user", tag="user")
class UserController:
    def __init__(self, service: UserService):
        self.service = service

    @Get("/", response_model=list[User])
    def get_user(self):
        return self.service.get_user()

    @Get("/{user_id}", response_model=User)
    def get_user_by_id(self, user_id: Param[uuid.UUID]):
        return self.service.get_user_by_id(user_id)

    @Post("/")
    def add_user(self, user: Body[User]):
        return self.service.add_user(user)

    @Get("/test/new-user/{user_id}")
    def test_new_user(self, user_id: Param[uuid.UUID]):
        return self.service.get_user_by_id(user_id)
