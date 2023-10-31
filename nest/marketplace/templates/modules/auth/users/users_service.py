
from src.auth.auth_model import User, UserLogin
from orm_config import config
from nest.core.decorators import db_request_handler
from functools import lru_cache
from fastapi.exceptions import HTTPException
from src.auth.auth_service import AuthService
from datetime import timedelta


@lru_cache()
class UsersService:
    def __init__(self):
        self.config = config
        self.session = self.config.get_db()
        self.auth_service = AuthService()

    @db_request_handler
    def register(self, user: User):
        # Check if user with the given username already exists
        existing_user = self.auth_service.get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        # Hash the user's password
        hashed_password = self.auth_service.get_password_hash(user.password)

        # Create new user entity
        user_entity = UserEntity(
            username=user.username,
            password=hashed_password,
            email=user.email
        )
        self.session.add(user_entity)
        self.session.commit()
        return user_entity.id

    @db_request_handler
    def login(self, user: UserLogin):
        db_user = self.auth_service.get_user_by_username(user.username)
        if not db_user or not self.auth_service.verify_password(user.password, db_user.password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        # Generate JWT token
        access_token_expires = timedelta(minutes=self.auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.auth_service.create_access_token(
            data={"sub": db_user.username}, expires_delta=access_token_expires
        )

        # Return the token
        return {"access_token": access_token, "token_type": "bearer"}
