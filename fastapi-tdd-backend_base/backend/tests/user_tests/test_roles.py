import pytest
from typing import List
import uuid

from databases import Database
from fastapi import FastAPI, status
from httpx import AsyncClient
from icecream import ic
from loguru import logger

from modules.users.roles.role_repositories import RoleRepository
from modules.users.roles.role_schemas import RoleCreate, RoleIn, RoleOut

pytestmark = pytest.mark.asyncio


@pytest.fixture
def new_role() -> RoleCreate:
    return RoleCreate(
        role="otro test role",
        permissions=["permissions:list-permissions", "roles:create-role"],
    )


@pytest.fixture
def other_new_role() -> RoleCreate:
    return RoleCreate(
        role="otro new role",
        permissions=["permissions:list-permissions", "roles:create-role"],
    )


@pytest.fixture
async def otro_test_role(db: Database) -> RoleOut:
    role_create = RoleIn(
        role="otro new role",
        permissions=["permissions:list-permissions", "roles:create-role"],
        created_by=uuid.uuid4(),
        updated_by=uuid.uuid4(),
    )

    role_repo = RoleRepository(db=db)
    return await role_repo.create_role(role_create)


class TestRoleRoutes:
    async def test_create_rol_route_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        res = await client.post(app.url_path_for("roles:create-role"), json={})
        assert res.status_code != status.HTTP_404_NOT_FOUND

    async def test_get_roles_route_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("roles:roles_list"))
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestCreateRole:
    async def test_valid_input_creates_role(
        self, app: FastAPI, authorized_client: AsyncClient, new_role: RoleCreate
    ) -> None:
        client = await authorized_client
        res = await client.post(
            app.url_path_for("roles:create-role"), json={"role": new_role.dict()}
        )

        assert res.status_code == status.HTTP_201_CREATED
        created_role = RoleOut(**res.json())

        assert created_role.id
        assert created_role.role == new_role.role
        assert len(created_role.permissions) == len(new_role.permissions)

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, 422),
            ({}, 422),
            ({"role": "test_rol"}, 422),
            ({"role": "", "permissions": ["test_perm_1", "test_perm_2"]}, 422),
            ({"role": "test_rol", "permissions": []}, 422),
            ({"role": "test_rol", "permissions": ["test_perm_1"]}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        invalid_payload: dict,
        status_code: int,
    ) -> None:
        client = await authorized_client
        res = await client.post(
            app.url_path_for("roles:create-role"), json={"role": invalid_payload}
        )
        assert res.status_code == status_code


class TestGetRolesList:
    async def test_get_roles_list(
        self,
        app: FastAPI,
        client: AsyncClient,
        authorized_client: AsyncClient,
        new_role: RoleCreate,
    ) -> None:
        client = await authorized_client
        res = await client.get(app.url_path_for("roles:roles_list"))

        assert res.status_code == status.HTTP_200_OK
        result = res.json()

        assert isinstance(result, dict)
        data = result.get("data")
        assert len(data) > 0

    # ["search", "page_number", "page_size", "order", "direction"]
    @pytest.mark.parametrize(
        "attrs, status",
        (
            ([None, 1, 10, None, None], 200),
            (["ASEGURADOS", 1, 10, None, None], 200),
            (["AFILIADOS", 1, 10, None, None], 200),
            (["CLIENTES", 1, 10, None, None], 200),
            (["PLANES", 1, 10, None, None], 200),
            (["REPORTES", 1, 10, None, None], 200),
            (["USUARIOS", 1, 10, None, None], 200),
            (["asegurados", 1, 10, None, None], 200),
            (["afiliados", 1, 10, None, None], 200),
            (["CLientes", 1, 10, None, None], 200),
            (["planES", 1, 10, None, None], 200),
            (["ReporTES", 1, 10, None, None], 200),
            (["USUArios", 1, 10, None, None], 200),
            (["usua", 1, 10, None, None], 200),
            (["plan", 1, 10, None, None], 200),
        ),
    )
    async def test_get_roles_list_filtered(
        self,
        app: FastAPI,
        client: AsyncClient,
        authorized_client: AsyncClient,
        attrs: List[str | None],
        status: int,
        search: str | None = None,
        order: str = None,
        direction: str = None,
    ) -> None:
        client = await authorized_client
        search = attrs[0]
        page_number = attrs[1]
        page_size = attrs[2]
        order = attrs[3]
        direction = attrs[4]
        base_url = "http://localhost:8000/api/v1/users/roles"

        if page_number:
            base_url += f"/?page_number={page_number}"

        if page_size:
            base_url += f"&page_size={page_size}"

        if order:
            base_url += f"&order={order}"

        if direction:
            base_url += f"&direction={direction}"

        if search:
            base_url += f"&search={search}"

        res = await client.get(base_url)

        assert res.status_code == status


class TestGetRoleById:
    async def test_get_role_by_id(
        self, app: FastAPI, authorized_client: AsyncClient, test_role: RoleOut
    ) -> None:
        client = await authorized_client
        role_in_db = await test_role
        res = await client.get(
            app.url_path_for("roles:get-role-by-id", id=role_in_db.id)
        )

        assert res.status_code == status.HTTP_200_OK
        assert (res.json()).get("id") == str(role_in_db.id)

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (None, 422),
            (" ", 422),
            (uuid.uuid4(), 404),
        ),
    )
    async def test_wrong_id_returns_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        id: uuid.UUID,
        status_code: int,
    ) -> None:
        client = await authorized_client
        res = await client.get(app.url_path_for("roles:get-role-by-id", id=id))
        assert res.status_code == status_code


class TestUpdateRole:
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
            (["role"], ["new fake role"]),
            (["permissions"], ["new fake permission", "new more fake permission"]),
            (
                ["role", "permissions"],
                [
                    "other new fake role",
                    ["other fake permission", "other more fake permission"],
                ],
            ),
        ),
    )
    async def test_update_role_with_valid_data(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        test_role: RoleOut,
        attrs_to_change: List[str],
        values: List[str],
    ) -> None:
        client = await authorized_client
        role_in_db = await test_role

        if attrs_to_change[0] == "role":
            rol_update = {"role_update": {attrs_to_change[0]: values[0]}}
        elif attrs_to_change[0] == "permissions":
            rol_update = {"role_update": {attrs_to_change[0]: values}}
        elif len(attrs_to_change) == 2:
            rol_update = {
                "role_update": {
                    attrs_to_change[0]: values[0],
                    attrs_to_change[1]: values[1],
                }
            }

        res = await client.put(
            app.url_path_for("roles:update-role-by-id", id=role_in_db.id),
            json=rol_update,
        )
        assert res.status_code == status.HTTP_200_OK
        role_updated_in_db = RoleOut(**res.json())
        assert role_in_db.id == role_updated_in_db.id

    @pytest.mark.parametrize(
        "payload, status_code",
        (
            ({"role": None}, 422),
            ({"role": " "}, 422),
            ({"role": "test_rol"}, 422),
            ({"role": "", "permissions": ["test_perm_1", "test_perm_2"]}, 422),
            ({"role": "test_rol", "permissions": []}, 422),
            ({"role": "test_rol", "permissions": ["test_perm_1"]}, 422),
        ),
    )
    async def test_update_role_with_invalid_input_throws_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        payload: dict,
        status_code: int,
        new_role: RoleCreate,
        db: Database,
    ) -> None:
        client = await authorized_client
        role_repo = RoleRepository(db)

        role_in_db = await role_repo.get_role_by_name(new_role.role)
        res = await client.put(
            app.url_path_for("roles:update-role-by-id", id=role_in_db.id), json=payload
        )

        assert res.status_code == status_code


class TestActivateDeactivateRole:
    async def test_can_update_role_is_active_successfully(
        self, app: FastAPI, authorized_client: AsyncClient, test_role: RoleOut
    ) -> None:
        client = await authorized_client
        role_test = await test_role
        role_update = {"role_update": {"is_active": False}}

        res = await client.put(
            app.url_path_for("roles:update-activate-role-by-id", id=role_test.id),
            json=role_update,
        )

        assert res.status_code == status.HTTP_200_OK

        res = await client.get(
            app.url_path_for("roles:get-role-by-id", id=role_test.id)
        )

        assert not (res.json()).get("is_active")

        role_update = {"role_update": {"is_active": True}}
        res = await client.put(
            app.url_path_for("roles:update-activate-role-by-id", id=role_test.id),
            json=role_update,
        )

        assert (res.json()).get("is_active")


class TestDeleteUser:
    async def test_can_delete_role_successfully(
        self, app: FastAPI, authorized_client: AsyncClient, otro_test_role: RoleOut
    ) -> None:
        client = await authorized_client
        role_test = await otro_test_role

        res = await client.delete(
            app.url_path_for("roles:delete-role-by-id", id=role_test.id)
        )

        assert res.status_code == status.HTTP_200_OK

        res = await client.get(
            app.url_path_for(
                "roles:get-role-by-id",
                id=role_test.id,
            ),
        )
        assert res.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (uuid.uuid4(), 404),
            (" ", 422),
            (None, 422),
            ("abc123", 422),
            ("123", 422),
        ),
    )
    async def test_delete_role_with_invalid_input_throws_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        id: uuid.UUID,
        status_code: int,
    ) -> None:
        client = await authorized_client

        res = await client.delete(app.url_path_for("roles:delete-role-by-id", id=id))

        assert res.status_code == status_code
