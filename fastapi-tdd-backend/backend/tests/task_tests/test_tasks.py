import pytest
from uuid import uuid4, UUID

from fastapi import FastAPI, status
from httpx import AsyncClient
from loguru import logger

from modules.tasks.task_schemas import (
    TaskCreate,
    TaskInDB,
    TaskToUpdate,
)


pytestmark = pytest.mark.asyncio


class TestTaskRoutes:
    async def test_create_task_route_exists(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        res = await client.post(app.url_path_for("tasks:create-task"), json={})
        assert res.status_code != status.HTTP_404_NOT_FOUND

class TestCreateTask:
    async def test_valid_input_creates_task(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
    ) -> None:
        client = await authorized_client

        res = await client.post(
            app.url_path_for("tasks:create-task"), json={"task": {"task_name": "test_task"}}
        )

        assert res.status_code == status.HTTP_201_CREATED
        data = res.json()
        assert data["id"] != None
        assert data["task_name"] == "test_task"


    @pytest.mark.parametrize(
        "attr, value, status_code",
        (
            ("task_name", None, 422),
            ("task_name", "", 422),
            ("task_name", "ab", 422),
        ),
    )
    async def test_invalid_input_reaise_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        attr: str,
        value: str,
        status_code: int
    ) -> None:
        client = await authorized_client
        new_task = {
            "task_name": ""
        }
        new_task[attr] = value
        res = await client.post(
            app.url_path_for("tasks:create-task"), json={"task": new_task}
        )

        assert res.status_code == status_code     


class TestGetTasks:
    async def test_get_tasks_list(
        self, app: FastAPI, authorized_client: AsyncClient
    ) -> None:
        client = await authorized_client

        res = await client.get(app.url_path_for("tasks:tasks_list"))

        assert res.status_code == status.HTTP_200_OK

        result = res.json()
        assert len(result) > 0


    async def test_get_task_by_id(
        self, 
        app: FastAPI, 
        authorized_client: AsyncClient, 
    ) -> None:
        client = await authorized_client

        # se crea una tarea de prueba para obtener el id de DB        
        test_task = {
            "task_name": "Otra test Task"
        }

        res1 = await client.post(
            app.url_path_for("tasks:create-task"), json={"task": test_task}
        )
        test_data = res1.json()
        test_id = str(test_data["id"])

        # aqui comienza la verdadera prueba
        res = await client.get(
            app.url_path_for("tasks:get-task-by-id", id=test_id)
        )
        assert res.status_code == status.HTTP_200_OK
        task = TaskInDB(**res.json())

        assert str(task.id) == test_id
        assert task.task_name == test_data["task_name"]
        

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (uuid4(), 404), 
            (None, 422), 
            ("abc123", 422)
        ),
    )
    async def test_wrong_id_returns_error(
        self, 
        app: FastAPI, 
        authorized_client: AsyncClient, 
        id: UUID, 
        status_code: int
    ) -> None:
        client = await authorized_client

        res = await client.get(app.url_path_for("tasks:get-task-by-id", id=id))

        assert res.status_code == status_code


class TestUpdateTask:
    async def test_update_task_with_valid_data(
        self,
        app: FastAPI,
        authorized_client: AsyncClient, 
        
    ) -> None:
        client = await authorized_client

        res1 = await client.get(
            app.url_path_for("tasks:tasks_list")
        )
        task_in_db = res1.json().get("data")[0]

        test_id = task_in_db.get("id")

        task_update = TaskToUpdate(
            task_name = "Nombre de prueba cambiado"
        )

        res = await client.put(
            app.url_path_for("tasks:update-task-by-id", id=test_id), json={"task_update": task_update.dict()}
        )
        assert res.status_code == status.HTTP_200_OK
        task_updated = res.json()
        assert task_updated["task_name"] == task_update.task_name

    @pytest.mark.parametrize(
        "attrs_to_change, value",
        (
            ("is_active", False),
            ("is_active", True),
        ),
    )
    async def test_deactivate_activate_task_with_valid_data(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        attrs_to_change: str,
        value: bool,
    ) -> None:
        client = await authorized_client
        
        res1 = await client.get(
            app.url_path_for("tasks:tasks_list")
        )
        task_in_db = res1.json().get("data")[0]
        test_id = task_in_db.get("id")

        task_update = {"task_update": {attrs_to_change: value}}
        res = await client.put(
            app.url_path_for("tasks:update-task-by-id", id=test_id), json={"task_update": task_update}
        )
        assert res.status_code == status.HTTP_200_OK


class TestDeleteTask:
    async def test_can_delete_task(self,
        app: FastAPI,
        authorized_client: AsyncClient,
    ) -> None:
        client = await authorized_client
        
        res1 = await client.post(
            app.url_path_for("tasks:create-task"), json={"task": {"task_name": "Tarea para borrar"}}
        )
        task_in_db = res1.json()

        test_id = task_in_db.get("id")

        res = await client.delete(
            app.url_path_for("tasks:delete-task-by-id", id=test_id)
        )
        assert res.status_code == status.HTTP_200_OK       