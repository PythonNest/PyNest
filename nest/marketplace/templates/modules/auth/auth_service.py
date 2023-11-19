AUTH_SERVICE_TEMPLATE = f"""from orm_config import config
from src.auth.auth_model import TokenData, Token
from functools import lru_cache
from nest.core.decorators import db_request_handler
from datetime import datetime, timedelta
from src.users.users_entity import User
import bcrypt
import jwt
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer




"""