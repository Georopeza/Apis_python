import pytest
from typing import List

from fastapi import FastAPI, status
from httpx import AsyncClient
from loguru import logger


pytestmark = pytest.mark.asyncio


class TestRutesPermissions:
    async def test_list_permissions_route_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        res = await client.get(app.url_path_for("permissions:list-permissions"))
        assert res.status_code != status.HTTP_404_NOT_FOUND


class TestGetPermissions:
    async def test_get_list_permissions_returns_valid_response(
        self, app: FastAPI, authorized_client: AsyncClient
    ) -> None:
        client = await authorized_client
        res = await client.get(app.url_path_for("permissions:list-permissions"))
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0
