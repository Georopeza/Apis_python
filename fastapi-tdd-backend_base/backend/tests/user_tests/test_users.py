import pytest
import jwt
from typing import List, Type
from uuid import uuid4, UUID

from databases import Database
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from icecream import ic
from loguru import logger
from pydantic import ValidationError
from starlette.datastructures import Secret

from modules.users.roles.role_repositories import RoleRepository
from modules.users.roles.role_schemas import RoleIn
from modules.users.auths.auth_exceptions import AuthExceptions
from modules.users.auths.auth_schemas import JWTCreds, JWTMeta, JWTPayload
from modules.users.auths.auth_services import AuthService
from modules.users.permissions.permissions_schemas import PermissionsOut
from modules.users.roles.role_schemas import RoleOut
from modules.users.users.user_schemas import (
    UserCreate,
    UserIn,
    UserOut,
    UserInDB,
    UserPublic,
)
from modules.users.users.user_services import UserService
from modules.users.users.user_repositories import UserRepository
from shared.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_AUDIENCE,
    SECRET_KEY,
    SUPER_ADMIN,
    SUPER_ROLE,
    SUPER_PASSWORD,
)
from shared.utils.crypto_credentials import CryptoAES
from shared.utils.service_result import ServiceResult


pytestmark = pytest.mark.asyncio


@pytest.fixture
async def new_user(db: Database) -> UserCreate:
    role: RoleIn = RoleIn(role="test rol", permissions=["testing:test-grant"])

    role_item = await RoleRepository(db).get_role_by_name(role.role)
    if not role_item:
        role_item = await RoleRepository(db).create_role(role)

    return UserCreate(
        fullname="Pepe Boveda",
        username="pepeboveda",
        email="pepeboveda@prueba.com",
        password="psw_super_secreto",
        is_superadmin=False,
        role_id=str(role_item.id),
    )


@pytest.fixture
async def otro_user(db: Database) -> UserCreate:
    role: RoleIn = RoleIn(role="otro test rol", permissions=["testing:test-grant"])

    role_item = await RoleRepository(db).get_role_by_name(role.role)
    if not role_item:
        role_item = await RoleRepository(db).create_role(role)

    return UserCreate(
        fullname="Juan Prueba",
        username="juanprueba",
        email="juanprueba@prueba.com",
        password="psw_super_secreto",
        is_superadmin=False,
        role_id=str(role_item.id),
    )


class TestSuperAdmin:
    async def test_verify_super_admin_exists(
        self, app: FastAPI, client: AsyncClient, db: Database
    ) -> None:
        super_admin = await UserRepository(db).get_user_by_username(
            username=SUPER_ADMIN
        )

        assert super_admin
        assert super_admin.username == SUPER_ADMIN
        assert super_admin.is_superadmin


class TestUserRoutes:
    async def test_create_user_route_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        res = await client.post(app.url_path_for("users:create-user"), json={})
        assert res.status_code != status.HTTP_404_NOT_FOUND

    async def test_users_list_route_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("users:users_list"))
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestCreateUser:
    async def test_valid_input_creates_user(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        db: Database,
        otro_user: UserCreate,
    ) -> None:
        client = await authorized_client

        # This is made it to avoid serialization error on UUID
        user_test = jsonable_encoder(await otro_user)
        user_repo = UserRepository(db)

        user_in_db = await user_repo.get_user_by_email(email=user_test.get("email"))
        assert user_in_db is None

        user_in_db = await user_repo.get_user_by_username(
            username=user_test.get("username")
        )
        assert user_in_db is None

        res = await client.post(
            app.url_path_for("users:create-user"), json={"user": user_test}
        )

        assert res.status_code == status.HTTP_201_CREATED

        # ensure the user now exists in db
        user_in_db = await user_repo.get_user_by_username(
            username=user_test.get("username")
        )

        assert user_in_db
        assert user_in_db.salt is not None and user_in_db.salt is not None
        assert user_in_db.username == user_test.get("username")
        assert user_in_db.email == user_test.get("email")
        assert AuthService().verify_password(
            password=user_test["password"],
            salt=user_in_db.salt,
            hashed_pw=user_in_db.password,
        )

        # # ensure the user returned is equal to the database
        created_user = UserOut(**res.json())
        assert created_user.id == user_in_db.id

    @pytest.mark.parametrize(
        "attr, value, status_code",
        (
            ("email", "tester@prueba.com", 400),
            ("username", "tester", 400),
            ("email", "invalid_email@one@two.com", 422),
            ("password", "corto", 422),
            ("username", "12@/%&rf#<>", 422),
            ("username", "ab", 422),
        ),
    )
    async def test_invalid_input_raises_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        db: Database,
        attr: str,
        value: str,
        status_code: int,
        # new_user: UserIn
    ) -> None:
        # user_serialized = jsonable_encoder(await new_user)
        new_test = {
            "fullname": "Pepe Boveda",
            "username": "pepeboveda",
            "email": "pepeboveda@prueba.com",
            "password": "psw_super_secreto",
            "is_superadmin": False,
            "role_id": str(uuid4()),
        }
        client = await authorized_client
        new_test[attr] = value
        res = await client.post(
            app.url_path_for("users:create-user"), json={"user": new_test}
        )
        assert res.status_code == status_code


class TestAuthTokens:
    async def test_can_create_access_token_successfully(
        self, app: FastAPI, client: AsyncClient, test_user: UserInDB
    ) -> None:
        user_to_test = await test_user

        access_token = AuthService().create_access_token_for_user(
            user=user_to_test,
            secret_key=str(SECRET_KEY),
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )

        creds = jwt.decode(
            access_token,
            str(SECRET_KEY),
            audience=JWT_AUDIENCE,
            algorithms=[JWT_ALGORITHM],
        )

        assert creds.get("username") is not None
        assert creds["username"] == user_to_test.username
        assert creds["aud"] == JWT_AUDIENCE

    async def test_token_missing_user_is_invalid(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        access_token = AuthService().create_access_token_for_user(
            user=None,
            secret_key=str(SECRET_KEY),
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        with pytest.raises(jwt.PyJWTError):
            jwt.decode(
                access_token,
                str(SECRET_KEY),
                audience=JWT_AUDIENCE,
                algorithms=[JWT_ALGORITHM],
            )

    @pytest.mark.parametrize(
        "secret_key, jwt_audience, exception",
        (
            ("wrong-secret", JWT_AUDIENCE, jwt.InvalidSignatureError),
            (None, JWT_AUDIENCE, jwt.InvalidSignatureError),
            (SECRET_KEY, "othersite:auth", jwt.InvalidAudienceError),
            (SECRET_KEY, None, ValidationError),
        ),
    )
    async def test_invalid_token_content_raises_error(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_user: UserInDB,
        secret_key: str | Secret,
        jwt_audience: str,
        exception: Type[BaseException],
    ) -> None:
        user_to_test = await test_user

        with pytest.raises(exception):
            access_token = AuthService().create_access_token_for_user(
                user=user_to_test,
                secret_key=str(secret_key),
                audience=jwt_audience,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES,
            )

            jwt.decode(
                access_token,
                str(SECRET_KEY),
                audience=JWT_AUDIENCE,
                algorithms=[JWT_ALGORITHM],
            )

    async def test_can_retrieve_username_from_token(
        self, app: FastAPI, client: AsyncClient, test_user: UserInDB
    ) -> None:
        user_test = await test_user

        token = AuthService().create_access_token_for_user(
            user=user_test, secret_key=str(SECRET_KEY)
        )
        username = AuthService().get_username_from_token(
            token=token, secret_key=str(SECRET_KEY)
        )
        assert username == user_test.username

    @pytest.mark.parametrize(
        "secret, wrong_token",
        (
            (SECRET_KEY, "asdf"),  # use wrong token
            (SECRET_KEY, ""),  # use wrong token
            (SECRET_KEY, None),  # use wrong token
            ("ABC123", "use correct token"),  # use wrong secret
        ),
    )
    async def test_error_when_token_or_secret_is_wrong(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_user: UserInDB,
        secret: Secret | str,
        wrong_token: str | None,
    ) -> None:
        user_test = await test_user
        token = AuthService().create_access_token_for_user(
            user=user_test, secret_key=str(SECRET_KEY)
        )

        if wrong_token == "use correct token":
            wrong_token = token

        with pytest.raises(AuthExceptions.AuthNoValidTokenCredentialsException):
            username = AuthService().get_username_from_token(
                token=wrong_token, secret_key=str(secret)
            )


class TestUserLogin:
    async def test_user_can_login_successfully_and_receives_valid_token(
        self, app: FastAPI, client: AsyncClient, new_user: UserInDB
    ) -> None:
        client.headers["content-type"] = "application/x-www-form-urlencoded"

        user_to_test = await new_user
        login_data = {"username": user_to_test.username, "password": user_to_test.password}

        res = await client.post(app.url_path_for("auth:login"), data=login_data)
        assert res.status_code == status.HTTP_200_OK
        # check that token exists in response and has user encoded within it
        token = res.json().get("access_token")
        creds = jwt.decode(
            token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM]
        )
        assert "username" in creds
        assert creds["username"] == user_to_test.username
        assert "sub" in creds
        assert creds["sub"] == user_to_test.email
        # check that token is proper type
        assert "token_type" in res.json()
        assert res.json().get("token_type") == "bearer"

    @pytest.mark.parametrize(
        "credential, wrong_value, status_code",
        (
            ("username", "wrong_username", 401),
            # ("username", None, 422),
            ("password", "wrongpassword", 401),
            # ("spassword", None, 422),
        ),
    )
    async def test_user_with_wrong_creds_doesnt_receive_token(
        self,
        app: FastAPI,
        client: AsyncClient,
        new_user: UserInDB,
        credential: str,
        wrong_value: str,
        status_code: int,
    ) -> None:
        client.headers["content-type"] = "application/x-www-form-urlencoded"
        user_data = (await new_user).dict()
        user_data["password"] = "psw_super_secreto" 
        user_data[credential] = wrong_value
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        res = await client.post(app.url_path_for("auth:login"), data=login_data)

        assert res.status_code == status_code
        assert "access_token" not in res.json()

    async def test_super_admin_can_login_successfully(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        client.headers["content-type"] = "application/x-www-form-urlencoded"

        login_data = {
            "username": SUPER_ADMIN,
            "password": SUPER_PASSWORD,
        }
        res = await client.post(app.url_path_for("auth:login"), data=login_data)
        assert res.status_code == status.HTTP_200_OK

        token = res.json().get("access_token")
        creds = jwt.decode(
            token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM]
        )
        assert "username" in creds
        assert creds["username"] == SUPER_ADMIN
        # check that token is proper type
        assert "token_type" in res.json()
        assert res.json().get("token_type") == "bearer"


class TestGetUsers:
    async def test_get_users_list(
        self, app: FastAPI, authorized_client: AsyncClient
    ) -> None:
        client = await authorized_client
        res = await client.get(app.url_path_for("users:users_list"))

        assert res.status_code == status.HTTP_200_OK

        result = res.json()
        assert len(result) > 0

    # @pytest.mark.parametrize(
    #     "search,page_number, page_size, order, direction, status_code",
    #     (
    #         (None,None, None, None, None, 200),
    #         (None,1,None, None, None, 200),
    #         (None,1,10, None, None, 200),
    #         (None,None,None, "fullname", None, 200),
    #         (None,None,None, "fullname", "DESC", 200),
    #         (None,None,None, "fullname", "ASC", 200),
    #         (None,None,None, "username", None, 200),
    #         (None,None,None, "username", "DESC", 200),
    #         (None,None,None, "username", "ASC", 200),
    #         (None,None,None, "email", None, 200),
    #         (None,None,None, "email", "DESC", 200),
    #         (None,None,None, "email", "ASC", 200),
    #         (None,None,None, "rol", None, 200),
    #         (None,None,None, "rol", "DESC", 200),
    #         (None,None,None, "rol", "ASC", 200),
    #     ),
    # )
    # async def test_get_users_list_with_parameters(
    #     self,
    #     app: FastAPI,
    #     authorized_client: AsyncClient,
    #     search: str,
    #     page_number: int,
    #     page_size: int,
    #     order,
    #     direction,
    #     status_code
    # ) -> None:
    #     client = await authorized_client
    #     res = await client.get(app.url_path_for("users:users_list",
    #                         search=search,
    #                         page_number=page_number,
    #                         page_size=page_size,
    #                         order=order,
    #                         direction=direction))
    #     assert res.status_code == status_code
    #     result = res.json()
    #     assert len(result) > 0

    async def test_get_user_by_id(
        self, app: FastAPI, authorized_client: AsyncClient, otro_test_user: UserInDB
    ) -> None:
        client = await authorized_client
        user_test = await otro_test_user

        res = await client.get(
            app.url_path_for("users:get-user-by-id", id=user_test.id)
        )
        assert res.status_code == status.HTTP_200_OK
        user = UserPublic(**res.json())

        assert user.id == user_test.id
        assert user.fullname == user_test.fullname
        assert user.email == user_test.email
        assert user.username == user_test.username

    @pytest.mark.parametrize(
        "id, status_code",
        ((uuid4(), 404), (None, 422), ("abc123", 422)),
    )
    async def test_wrong_id_returns_error(
        self, app: FastAPI, authorized_client: AsyncClient, id: UUID, status_code: int
    ) -> None:
        client = await authorized_client

        res = await client.get(app.url_path_for("users:get-user-by-id", id=id))

        assert res.status_code == status_code


class TestUsersAuth:
    async def test_authenticated_user_can_view_permissions(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
    ) -> None:
        authorized_client = await authorized_client

        res = await authorized_client.get(
            app.url_path_for("permissions:list-permissions")
        )
        assert res.status_code == status.HTTP_200_OK

        result = [PermissionsOut(**item) for item in res.json()]
        assert result


class TestUpdateUser:
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
            (["fullname"], ["a user with strange name"]),
            (["username"], ["afunnyusername"]),
            (["email"], ["funny@test.com"]),
            (["password"], ["funny@test.com"]),
            (["is_superadmin"], [False]),
            (["fullname", "username"], ["new full", "newusername"]),
            (["username", "password"], ["other_suername", "strange$$psw"]),
            (["email", "password"], ["ugly@prueba.com", "strange$$psw"]),
            (["password", "is_superadmin"], ["strange$$psw", True]),
            (
                ["fullname", "username", "email", "password", "is_superadmin"],
                (
                    [
                        "pedro Picapiedra",
                        "pedropicapiedra",
                        "picapiedra@test.com",
                        "rocadura_@",
                        False,
                    ]
                ),
            ),
        ),
    )
    async def test_update_user_with_valid_data(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        otro_test_user: UserInDB,
        attrs_to_change: List[str],
        values: List[str],
        db: Database,
    ) -> None:
        client = await authorized_client

        user_repo = UserRepository(db)
        user_in_db = await otro_test_user

        id_in_db = user_in_db.id

        for attr, value in zip(attrs_to_change, values):
            user_update = {"user_update": {attr: value}}

        res = await client.put(
            app.url_path_for("users:update-user-by-id", id=id_in_db), json=user_update
        )
        assert res.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "attrs_to_change, value",
        (
            ("is_active", False),
            ("is_active", True),
        ),
    )
    async def test_deactivate_activate_user_with_valid_data(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        otro_test_user: UserInDB,
        attrs_to_change: str,
        value: bool,
        db: Database,
    ) -> None:
        client = await authorized_client
        user_in_db = await otro_test_user
        id_in_db = user_in_db.id

        user_update = {"user_update": {attrs_to_change: value}}
        res = await client.put(
            app.url_path_for("users:activate-user-by-id", id=id_in_db), json=user_update
        )
        assert res.status_code == status.HTTP_200_OK


class TestDeleteUser:
    async def test_can_delete_user_successfully(
        self, app: FastAPI, authorized_client: AsyncClient, otro_test_user: UserInDB
    ) -> None:
        client = await authorized_client
        user_test = await otro_test_user

        res = await client.delete(
            app.url_path_for("users:delete-user-by-id", id=user_test.id)
        )

        assert res.status_code == status.HTTP_200_OK

        res = await client.get(
            app.url_path_for(
                "users:get-user-by-id",
                id=user_test.id,
            ),
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (uuid4(), 404),
            (" ", 422),
            (None, 422),
            ("abc123", 422),
            ("123", 422),
        ),
    )
    async def test_delete_user_with_invalid_input_throws_error(
        self, app: FastAPI, authorized_client: AsyncClient, id: UUID, status_code: int
    ) -> None:
        client = await authorized_client

        res = await client.delete(app.url_path_for("users:delete-user-by-id", id=id))

        assert res.status_code == status_code
