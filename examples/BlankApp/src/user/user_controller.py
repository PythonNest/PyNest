# app/controllers/user_controller.py

import uuid
from typing import Optional, Any
from .user_service import UserService
from nest.core import Controller, Get, Post, Param, Query, Body, Form, File
from .user_model import UserCreateDTO, UserDTO


@Controller(prefix="/users", tag="Users")
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @Get("/{user_id}")
    def get_user_by_id(self, user_id: Param[uuid.UUID]) -> dict:
        """
        Retrieve a user by their UUID.
        """
        user = self.user_service.get_user_by_id(str(user_id))
        return {"user": user}

    @Get("/")
    def list_users(
        self,
        page: Query[int] = 1,
        limit: Query[int] = 50,
        search: Optional[Query[str]] = None,
    ) -> dict:
        """
        List users with pagination and optional search.
        """
        # Implement pagination and search logic here
        return {
            "message": f"Listing users on page={page}, limit={limit}, search={search}"
        }

    @Post("/")
    def create_user(self, user: Body[UserCreateDTO]) -> dict:
        """
        Create a new user.
        """
        user_data = self.user_service.add_user(user)
        return {"message": "User created", "user": user_data}

    #
    @Post("/{user_id}/upload-avatar")
    def upload_avatar(
        self,
        user_id: Param[uuid.UUID],
        file: File[bytes],
        description: Optional[Form[str]] = None,
    ) -> dict:
        """
        Upload an avatar for a user.
        """
        # avatar_url = self.user_service.upload_avatar(user_id, file, description)
        print(f"Uploaded avatar for user {user_id}: {file}")
        print(f"Description: {description}")
        return {
            "message": "Avatar uploaded",
            "avatar_url": "http://example.com/avatar.jpg",
        }
