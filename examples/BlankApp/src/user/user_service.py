import time

from nest.core.decorators import Injectable

from .user_model import UserDTO, UserCreateDTO


@Injectable
class UserService:
    def __init__(self):
        self.database = []

    def get_user(self) -> list[UserDTO]:
        return self.database

    def add_user(self, user: UserCreateDTO):
        self.database.append(user)
        return user

    def get_user_by_id(self, user_id: str) -> UserDTO:
        return next((user for user in self.database if user.id == user_id), None)

    def log_access(self, user_id):
        print(user_id, " Access app")
