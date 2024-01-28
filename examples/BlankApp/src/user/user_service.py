from .user_model import User
from functools import lru_cache
from nest.core.decorators import Injectable


@lru_cache()
@Injectable
class UserService:
    def __init__(self):
        self.database = []

    def get_user(self):
        return self.database

    def add_user(self, user: User):
        self.database.append(user)
        return user
