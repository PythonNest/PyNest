import time

from nest.core import Injectable

from .user_model import User


@Injectable
class UserService:
    def __init__(self):
        self.database = []

    def get_user(self):
        return self.database

    def add_user(self, user: User):
        self.database.append(user)
        return user
