from typing import List
from uuid import UUID

from databases import Database
from icecream import ic
from loguru import logger
from modules.users.auths.auth_services import AuthService
from modules.users.roles.role_repositories import RoleRepository
from modules.users.users.user_exceptions import UserExceptions
from modules.users.users.user_repositories import UserRepository
from modules.users.users.user_schemas import (
    UserActivate,
    UserIn,
    UserInDB,
    UserOut,
    UserPublic,
    UserToSave,
    UserUpdate,
    UserUpdateDB,
)
from passlib.context import CryptContext
from shared.core.config import API_PREFIX
from shared.utils.service_result import ServiceResult
from shared.utils.short_pagination import short_pagination
from shared.utils.verify_uuid import is_valid_uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def create_user(self, user: UserToSave) -> ServiceResult:
        user_in = UserIn(**user.dict())
        user_in.salt = ""

        user = user_in

        if not user.role_id:
            logger.error("Try to create a User with no role assigned")
            return ServiceResult(UserExceptions.UserWithNoRoleException())

        if not user.username:
            logger.error("Try to create a User with username")
            return ServiceResult(UserExceptions.UserWithNoUsernameException())

        if not user.password or len(user.password) < 7:
            logger.error("Invalid password")
            return ServiceResult(UserExceptions.UserWithNoValidPasswordException())

        if user.is_superadmin is None:
            logger.error("Try to create a User with no user  type information")
            return ServiceResult(UserExceptions.UserWithNoUserTypeException())

        user_repo = UserRepository(self.db)

        # validates iis not existing in db
        if await user_repo.get_user_by_email(user.email):
            logger.error(f"Try to create a User with an existing email: {user.email}")
            return ServiceResult(UserExceptions.UserEmailAlreadyExistsExeption())

        if await user_repo.get_user_by_username(user.username):
            logger.error(f"Try to create a User with an existing username: {user.username}")
            return ServiceResult(UserExceptions.UserUsernameAlreadyExistsExeption())

        user_password_update = AuthService().create_salt_and_hashedpassword(
            plaintext_password=user.password
        )
        user.password = user_password_update.password
        user.salt = user_password_update.salt

        user.username = user.username.lower()

        user_item = await user_repo.create_user(user)
        if not user_item:
            logger.error("Error in DB creating a user")
            return ServiceResult(UserExceptions.UserCreateExcepton())

        role_repo = RoleRepository(db=self.db)
        role = await role_repo.get_role_by_id(user_item.id)
        if not role:
            user_item.role = None
        else:
            user_item.role = role.role

        return ServiceResult(user_item)

    async def get_users_list(
        self,
        search: str | None,
        page_num: int = 1,
        page_size: int = 10,
        order: str = None,
        direction: str = None,
    ) -> ServiceResult:
        users = await UserRepository(self.db).get_users_list(search, order, direction)

        service_result = None
        if len(users) == 0:
            users_list = []
            service_result = ServiceResult(users_list)
            service_result.status_code = 204
        else:
            users_list = [UserOut(**item.dict()) for item in users]
            response = short_pagination(
                page_num=page_num,
                page_size=page_size,
                data_list=users_list,
                route=f"{API_PREFIX}/users",
            )
            service_result = ServiceResult(response)

        return service_result

    async def get_user_by_id(self, id: UUID) -> ServiceResult:
        user = await UserRepository(self.db).get_user_by_id(id=id)

        if isinstance(user, dict) and not user.get("id"):
            logger.info("El usuario solicitado no está en base de datos")
            return ServiceResult(UserExceptions.UserNotFoundException())

        user_public = UserPublic(**user.dict())
        return ServiceResult(user_public)

    async def update_user(
        self, id: UUID, user_update: UserUpdate, current_user: UserInDB
    ) -> ServiceResult:
        if not is_valid_uuid(id):
            return ServiceResult(UserExceptions.UserIdNoValidException())

        credentials = {}
        try:
            if user_update.password:
                user_password_update = AuthService().create_salt_and_hashedpassword(
                    plaintext_password=user_update.password
                )
                credentials["password"] = user_password_update.password
                credentials["salt"] = user_password_update.salt

            user = await UserRepository(self.db).update_user(
                id=id,
                user_update=user_update,
                updated_by_id=current_user.id,
                credentials=credentials,
            )

            if isinstance(user, dict) and not user.get("id"):
                logger.info("El usuario a actualizar no está en base de datos")
                return ServiceResult(UserExceptions.UserNotFoundException())

            user_public = UserPublic(**user.dict())
            return ServiceResult(user_public)

        except Exception as e:
            logger.error(f"Se produjo un error: {e}")
            return ServiceResult(UserExceptions.UserInvalidUpdateParamsException(e))

    async def activate_user(
        self, id: UUID, user_update: UserActivate, current_user: UserInDB
    ) -> ServiceResult:
        if not is_valid_uuid(id):
            return ServiceResult(UserExceptions.UserIdNoValidException())

        user = await UserRepository(self.db).update_user(
            id=id,
            user_update=user_update,
            updated_by_id=current_user.id,
            credentials={},
        )

        if isinstance(user, dict) and not user.get("id"):
            logger.info("El usuario a activar / desactivar no está en base de datos")
            return ServiceResult(UserExceptions.UserNotFoundException())

        user_public = UserPublic(**user.dict())
        return ServiceResult(user_public)

    async def delete_user(
        self,
        id: UUID,
    ) -> ServiceResult:
        if not is_valid_uuid(id):
            return ServiceResult(UserExceptions.UserIdNoValidException())

        user_id = await UserRepository(self.db).delete_user(id=id)

        if isinstance(user_id, dict) and not user_id:
            logger.info("El usuario a eliminar no está en base de datos")
            return ServiceResult(UserExceptions.UserNotFoundException())

        return ServiceResult(user_id)

    async def change_password_by_id(
        self, id: UUID, psw_update: str, current_user: UserInDB
    ) -> ServiceResult:
        if not is_valid_uuid(id):
            return ServiceResult(UserExceptions.UserIdNoValidException())

        credentials = {}
        try:
            user_password_update = AuthService().create_salt_and_hashedpassword(
                plaintext_password=psw_update
            )
            credentials["password"] = user_password_update.password
            credentials["salt"] = user_password_update.salt

            user = await UserRepository(self.db).change_password_by_id(
                id=id,
                credentials=credentials,
            )

            if isinstance(user, dict) and not user.get("id"):
                logger.info("El usuario a actualizar no está en base de datos")
                return ServiceResult(UserExceptions.UserNotFoundException())

            user_public = UserPublic(**user.dict())
            return ServiceResult(user_public)

        except Exception as e:
            logger.error(f"Se produjo un error: {e}")
            return ServiceResult(UserExceptions.UserInvalidUpdateParamsException())
