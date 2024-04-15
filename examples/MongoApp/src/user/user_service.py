from nest.core import Injectable
from nest.core.decorators.database import db_request_handler

from .user_entity import User as UserEntity
from .user_model import User


@Injectable
class UserService:
    @db_request_handler
    async def add_user(self, user: User):
        new_user = UserEntity(**user.dict())
        await new_user.save()
        return new_user.id

    @db_request_handler
    async def get_user(self):
        return await UserEntity.find_all().to_list()
