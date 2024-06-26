import os
from typing import List
from uuid import uuid4
import warnings

import alembic
from alembic.config import Config
from asgi_lifespan import LifespanManager

from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient
from icecream import ic
from loguru import logger
import pytest
import pytest_asyncio

from modules.users.auths.auth_services import AuthService
from modules.users.roles.role_repositories import RoleRepository
from modules.users.roles.role_schemas import RoleIn, RoleOut
from modules.users.users.user_repositories import UserRepository
from modules.users.users.user_services import UserService
from modules.users.users.user_schemas import UserCreate, UserInDB
from shared.core.config import JWT_TOKEN_PREFIX, SECRET_KEY


# Aplicar migraciones al comienzo y fin de la sesión de pruebas
@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


# Se crea una nueva aplicación para pruebas
@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from shared.core.server import get_application

    return get_application()


# Se obtiene una referencia a la base de datos cuando se haga necesario
@pytest.fixture
def db(app: FastAPI) -> Database:
    return app.state._db


@pytest.fixture
async def test_user(db: Database) -> UserInDB:
    role_repo = RoleRepository(db)
    user_repo = UserRepository(db)
    user_service = UserService(db)

    new_role = RoleIn(
        role="test role",
        permissions=["permissions:list-permissions", "roles:create-role"],
    )

    # role_item = None
    existing_role = await role_repo.get_role_by_name(role=new_role.role)
    if not existing_role:
        role_item = await RoleRepository(db).create_role(new_role)
    else:
        role_item = existing_role

    new_user = UserCreate(
        fullname="Pepe Boveda",
        username="pepeboveda",
        email="pepeboveda@prueba.com",
        password="psw_super_secreto",
        is_superadmin=True,
        role_id=role_item.id,
    )

    existing_user = await user_repo.get_user_by_username(username=new_user.username)
    if existing_user:
        return existing_user

    user_created = await user_service.create_user(user=new_user)
    return user_created.value


@pytest.fixture
async def otro_test_user(db: Database) -> UserInDB:
    role_repo = RoleRepository(db)
    user_repo = UserRepository(db)
    user_service = UserService(db)

    new_role = RoleIn(
        role="test role",
        permissions=["permissions:list-permissions", "roles:create-role"],
    )

    # role_item = None
    existing_role = await role_repo.get_role_by_name(role=new_role.role)
    if not existing_role:
        role_item = await RoleRepository(db).create_role(new_role)
    else:
        role_item = existing_role

    new_user = UserCreate(
        fullname="Diego de la Vega",
        username="delavegad",
        email="delavegad@prueba.com",
        password="psw_super_secreto",
        is_superadmin=True,
        role_id=role_item.id,
    )

    existing_user = await user_repo.get_user_by_username(username=new_user.username)
    if existing_user:
        return existing_user

    existing_user = await user_repo.get_user_by_email(email=new_user.email)
    if existing_user:
        return existing_user

    user_created = await user_service.create_user(user=new_user)
    return user_created.value


# Hacer request en los tests
@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        ) as client:
            yield client


@pytest.fixture
async def authorized_client(client: AsyncClient, test_user: UserInDB) -> AsyncClient:

    user_test = await test_user

    access_token = AuthService().create_access_token_for_user(
        user=user_test, secret_key=str(SECRET_KEY)
    )

    client.headers = {
        **client.headers,
        "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}",
    }

    return client


@pytest.fixture
async def test_role(db: Database) -> RoleOut:
    role_repo = RoleRepository(db=db)
    role = RoleIn(
        role="fake role name",
        permissions=["permissions:list-permissions", "roles:create-role"],
    )
    role_in_db = await role_repo.get_role_by_name(role="fake role name")
    if role_in_db:
        return role_in_db
    return await role_repo.create_role(role=role)

