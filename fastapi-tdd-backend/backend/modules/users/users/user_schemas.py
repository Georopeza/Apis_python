from typing import List
from uuid import UUID

from modules.users.auths.auth_schemas import AccessToken
from pydantic import EmailStr, constr
from shared.utils.schemas_base import BaseSchema, DateTimeModelMixin, IDModelMixin


class UserBase(BaseSchema):
    fullname: str | None
    username: str | None
    email: EmailStr | None
    role_id: UUID | None


class UserCreate(BaseSchema):
    fullname: str
    username: constr(min_length=3, regex="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: constr(min_length=7, max_length=80)
    is_superadmin: bool = False
    is_active: bool = True
    role_id: UUID


class UserToSave(UserCreate):
    created_by: UUID | None
    updated_by: UUID | None


class UserInDB(IDModelMixin, DateTimeModelMixin):
    id: UUID
    fullname: str
    username: str
    email: EmailStr
    is_active: bool
    is_superadmin: bool
    password: constr(min_length=7, max_length=80)
    salt: str
    role_id: UUID
    role: str | None
    permissions: List | None
    created_by: UUID | str | None
    updated_by: UUID | str | None


class UserIn(UserBase):
    fullname: str
    username: constr(min_length=3, regex="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: constr(min_length=7, max_length=80)
    is_superadmin: bool = False
    role_id: UUID
    created_by: UUID | None
    updated_by: UUID | None
    salt: str | None


class UserPasswordUpdate(BaseSchema):
    password: constr(min_length=7, max_length=80)
    salt: str


class UserOut(IDModelMixin, BaseSchema):
    fullname: str
    username: constr(min_length=3, regex="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    role: str | None
    role_id: UUID | None
    is_active: bool
    created_by: str | None
    updated_by: str | None


class UserPublic(IDModelMixin, DateTimeModelMixin):
    fullname: str
    username: str
    email: EmailStr
    role_id: UUID
    is_active: bool
    is_superadmin: bool


class UserUpdate(UserBase):
    password: constr(min_length=7, max_length=80) | None


class UserUpdateDB(UserUpdate):
    salt: str | None


class UserActivate(BaseSchema):
    is_active: bool
