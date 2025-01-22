import time

from nest.core.decorators import Injectable

from .user_model import User


@Injectable
class UserService:
    def __init__(self):
        self.database = []
        time.sleep(5)
        print("UserService initialized")

    def get_user(self):
        return self.database

    def add_user(self, user: User):
        self.database.append(user)
        return user

    def get_user_by_id(self, user_id: str):
        return next((user for user in self.database if user.id == user_id), None)
