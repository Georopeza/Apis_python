from datetime import datetime
from typing import List, Type
from uuid import UUID

from databases import Database
from icecream import ic
from loguru import logger
from modules.users.users.user_exceptions import UserExceptions
from modules.users.users.user_schemas import UserIn, UserInDB, UserUpdateDB
from shared.utils.record_to_dict import record_to_dict
from shared.utils.repositories_base import BaseRepository


class UserRepository(BaseRepository):
    @property
    def _schema_out(self) -> Type[UserInDB]:
        return UserInDB

    @property
    def _schema_in(self) -> Type[UserIn]:
        return UserIn

    async def create_user(self, user: UserIn) -> UserInDB:
        from modules.users.users.user_sqlstaments import CREATE_USER_ITEM

        values = self.preprocess_create(user.dict())
        record = await self.db.fetch_one(query=CREATE_USER_ITEM, values=values)

        result = record_to_dict(record)

        return self._schema_out(**result)

    async def get_user_by_email(self, email: str) -> UserInDB:
        from modules.users.users.user_sqlstaments import GET_USER_BY_EMAIL

        values = {"email": email}
        record = await self.db.fetch_one(query=GET_USER_BY_EMAIL, values=values)

        if not record:
            return None

        return self._schema_out(**dict(record))

    async def get_user_by_username(self, username: str) -> UserInDB:
        from modules.users.users.user_sqlstaments import GET_USER_BY_USERNAME

        values = {"username": username}
        record = await self.db.fetch_one(query=GET_USER_BY_USERNAME, values=values)

        if not record:
            return None

        return self._schema_out(**dict(record))

    async def get_user_by_id(self, id: UUID) -> UserInDB | dict:
        from modules.users.users.user_sqlstaments import GET_USER_BY_ID

        values = {"id": id}
        record = await self.db.fetch_one(query=GET_USER_BY_ID, values=values)
        if not record:
            return {}

        user_in_db = record_to_dict(record)
        return self._schema_out(**user_in_db)

    async def get_users_list(
        self,
        search: str | None,
        order: str | None,
        direction: str | None,
    ) -> List[UserInDB]:
        from modules.users.users.user_sqlstaments import (
            GET_USERS_LIST,
            user_list_complements,
            user_list_search,
        )

        order = order.lower() if order != None else None
        direction = direction.upper() if order != None else None
        values = {}
        sql_sentence = user_list_complements(order, direction)
        sql_search = user_list_search()

        if not search:
            sql_sentence = GET_USERS_LIST + sql_sentence
        else:
            sql_sentence = GET_USERS_LIST + sql_search + sql_sentence
            values["search"] = "%" + search + "%"

        records = await self.db.fetch_all(query=sql_sentence, values=values)

        if len(records) == 0:
            return []

        if not records:
            return None

        return [self._schema_out(**dict(record)) for record in records]

    async def update_user(
        self,
        id: UUID,
        user_update: UserUpdateDB,
        updated_by_id: UUID,
        credentials: dict | None,
    ) -> UserInDB | dict:
        from modules.users.users.user_sqlstaments import UPDATE_USER_BY_ID

        user = await self.get_user_by_id(id=id)
        if not user:
            return {}

        user_update_params = user.copy(update=user_update.dict(exclude_unset=True))

        user_params_dict = user_update_params.dict()
        user_params_dict.pop("role")
        user_params_dict.pop("permissions")
        user_params_dict["updated_by"] = updated_by_id
        user_params_dict["updated_at"] = self._preprocess_date()
        if len(credentials) > 0:
            user_params_dict["password"] = credentials.get("password")
            user_params_dict["salt"] = credentials.get("salt")

        try:
            record = await self.db.fetch_one(query=UPDATE_USER_BY_ID, values=user_params_dict)
            user_updated = record_to_dict(record)
            return await self.get_user_by_id(id=user_updated.get("id"))
        except Exception as e:
            logger.error(f"Datos inválidos para actualizar un usuario: {e}")
            raise UserExceptions.UserInvalidUpdateParamsException()

    async def delete_user(
        self,
        id: UUID,
    ) -> str | dict:
        from modules.users.users.user_sqlstaments import DELETE_USER_BY_ID

        user = await self.get_user_by_id(id=id)
        if not user:
            return {}

        deleted_id = await self.db.execute(query=DELETE_USER_BY_ID, values={"id": id})

        return deleted_id

    async def get_users_by_role_id(self, role_id: UUID) -> List | dict:
        from modules.users.users.user_sqlstaments import GET_USERS_LIST_BY_ROLE_ID

        values = {"role_id": role_id}
        records = await self.db.fetch_all(query=GET_USERS_LIST_BY_ROLE_ID, values=values)

        if len(records) == 0:
            return []

        if not records:
            return None

        users = [dict(record) for record in records]
        logger.debug(f"los usuarios son: {users}")

        return [self._schema_out(**dict(record)) for record in records]

    async def change_password_by_id(
        self,
        id: UUID,
        credentials: dict | None,
    ) -> UserInDB | dict:
        from modules.users.users.user_sqlstaments import UPDATE_PSW_BY_ID

        user = await self.get_user_by_id(id=id)
        if not user:
            return {}

        user_update_params = user

        user_params_dict = user_update_params.dict()
        user_params_dict["updated_by"] = id
        user_params_dict["updated_at"] = self._preprocess_date()
        user_params_dict["password"] = credentials.get("password")
        user_params_dict["salt"] = credentials.get("salt")

        user_params_dict.pop("created_at")
        user_params_dict.pop("created_by")
        user_params_dict.pop("fullname")
        user_params_dict.pop("email")
        user_params_dict.pop("is_active")
        user_params_dict.pop("is_superadmin")
        user_params_dict.pop("role_id")
        user_params_dict.pop("role")
        user_params_dict.pop("permissions")
        user_params_dict.pop("username")

        try:
            record = await self.db.fetch_one(query=UPDATE_PSW_BY_ID, values=user_params_dict)
            user_updated = record_to_dict(record)
            return await self.get_user_by_id(id=user_updated.get("id"))
        except Exception as e:
            logger.error(f"Datos inválidos para actualizar el password del usuario: {e}")
            raise UserExceptions.UserInvalidUpdateParamsException()
