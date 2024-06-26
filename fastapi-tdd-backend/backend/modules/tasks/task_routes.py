from databases import Database
from fastapi import APIRouter, Body, Depends, Path, status
from loguru import logger
from typing import Dict
from uuid import UUID

from modules.tasks.task_services import TaskService
from modules.tasks.task_schemas import (
    TaskCreate,
    TaskInDB,
    TaskToUpdate,
)
from modules.users.users.user_schemas import (
    UserInDB
)
from modules.users.auths.auth_dependencies import get_current_active_user
from modules.users.auths.auth_exceptions import AuthExceptions
from shared.core.db.db_dependencies import get_database
from shared.utils.service_result import ServiceResult, handle_result
from shared.utils.verify_auth import is_authorized

task_router = APIRouter(
	prefix="/tasks",
	tags=["tasks"],	
    responses={404: {"description": "Not found"}},
)

@task_router.post(
    "/",
    response_model=TaskInDB,
    name="tasks:create-task",
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: TaskCreate = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "tasks:create-task"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))
    
    result = await TaskService(db).create_task(task, current_user)
    return handle_result(result)


@task_router.get(
    "/",  
    name="tasks:tasks_list", 
    status_code=status.HTTP_200_OK
)
async def get_tasks_list(
    search: str | None = None,
    page_number: int = 1,
    page_size: int = 10,
    order: str = "",
    direction: str = "",
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "tasks:get_tasks_list"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await TaskService(db).get_tasks_list(
        search,
        page_num=page_number,
        page_size=page_size,
        order=order,
        direction=direction,
    )
    return handle_result(result)


@task_router.get(
    "/{id}", 
    response_model=Dict, 
    name="tasks:get-task-by-id")
async def get_task_by_id(
    id: UUID = Path(..., title="The id of the task to get"),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "users:get-task-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await TaskService(db).get_task_by_id(id=id)
    return handle_result(result)

@task_router.put(
    "/{id}", 
    response_model=Dict, 
    name="tasks:update-task-by-id"
)
async def update_task_by_id(
    id: UUID = Path(..., title="The id of the task to update"),
    task_update: TaskToUpdate = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "tasks:update-task-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await TaskService(db).update_task(
        id=id, task_update=task_update, current_user=current_user
    )
    return handle_result(result)

@task_router.delete(
    "/{id}", 
    response_model=Dict, 
    name="tasks:delete-task-by-id"
)
async def delete_task_by_id(
    id: UUID = Path(..., title="The id of the task to update"),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "tasks:delete-task-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await TaskService(db).delete_task_by_id(
        id=id
    )
    return handle_result(result)