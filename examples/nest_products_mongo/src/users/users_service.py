from examples.nest_products_mongo.src.users.users_model import User
from examples.nest_products_mongo.src.users.users_entity import User as UserEntity
from nest.core.decorators import db_request_handler


class UsersService:

    @db_request_handler
    def add_user(self, user: User):
        user_entity = UserEntity(
            name=user.name, email=user.email, password=user.password
        )
        user_entity.save()
        return user_entity.id

    @db_request_handler
    def get_users(self):
        return UserEntity.find_all()

    @db_request_handler
    def get_user(self, user_id: int):
        return UserEntity.find_one({"_id": user_id})
