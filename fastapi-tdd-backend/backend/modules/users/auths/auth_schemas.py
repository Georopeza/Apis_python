from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from pydantic import EmailStr
from shared.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_AUDIENCE
from shared.utils.schemas_base import BaseSchema


class JWTMeta(BaseSchema):
    iss: str = "ucab.edu.ve"
    aud: str = JWT_AUDIENCE
    iat: float = datetime.timestamp(datetime.utcnow())
    exp: float = datetime.timestamp(
        datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


class JWTCreds(BaseSchema):
    """How we'll identify users"""

    sub: EmailStr
    username: str


class JWTPayload(JWTMeta, JWTCreds):
    """
    JWT Payload right before it's encoded - combine meta and username
    """

    pass


class AccessToken(BaseSchema):
    access_token: str
    token_type: str


class AuthResponse(AccessToken):
    id: UUID
    fullname: str
    username: str
    role: str
    permissions: List[str]


class AuthEmailRecoverPsw(BaseSchema):
    email: EmailStr


class AuthResetPsw(BaseSchema):
    new_psw: str
