from src.users.users_model import User
from src.users.users_entity import User as UserEntity
from nest.core.database.orm_config import config
from nest.core.decorators import db_request_handler, Injectable

@Injectable
class UsersService:
    def __init__(self):
        self.config = config
        self.session = self.config.get_db()

    @db_request_handler
    def add_user(self, user: User):
        user_entity = UserEntity(
            name=user.name, email=user.email, password=user.password
        )
        self.session.add(user_entity)
        self.session.commit()
        return user_entity.id

    @db_request_handler
    def get_users(self):
        return self.session.query(UserEntity).all()

    @db_request_handler
    def get_user(self, user_id: int):
        return self.session.query(UserEntity).filter(UserEntity.id == user_id).first()
