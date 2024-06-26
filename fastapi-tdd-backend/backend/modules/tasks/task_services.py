from databases import Database
from loguru import logger
from uuid import UUID

from shared.utils.verify_uuid import is_valid_uuid
from shared.utils.service_result import ServiceResult
from modules.tasks.task_exceptions import TaskExceptions
from modules.tasks.task_repositories import TaskRepository
from modules.tasks.task_schemas import (
    TaskCreate,
    TaskToSave,
    TaskInDB,
    TaskToUpdate
)
from modules.users.users.user_schemas import (
    UserInDB
)
from shared.core.config import API_PREFIX
from shared.utils.short_pagination import short_pagination


class TaskService:
    def __init__(self, db: Database):
        self.db = db

    async def create_task(self, task: TaskCreate, current_user: UserInDB):
        new_task = TaskToSave(**task.dict())
        new_task.created_by = current_user.id
        new_task.updated_by = current_user.id

        task_item = await TaskRepository(self.db).create_task(new_task)
        if not task_item:
            logger.error("Error in DB creating a task")
            return ServiceResult(TaskExceptions.TaskCreateExcepton())
        
        return ServiceResult(task_item)
    
    async def get_tasks_list(
        self,
        search: str | None,
        page_num: int = 1,
        page_size: int = 10,
        order: str = None,
        direction: str = None,
    ) -> ServiceResult:
        tasks = await TaskRepository(self.db).get_tasks_list(search, order, direction)

        service_result = None
        if len(tasks) == 0:
            service_result = ServiceResult([])
            service_result.status_code = 204
        else:
            response = short_pagination(
                page_num=page_num,
                page_size=page_size,
                data_list=tasks,
                route=f"{API_PREFIX}/tasks",
            )
            service_result = ServiceResult(response)

        return service_result

    
    async def get_task_by_id(self, id: UUID) -> ServiceResult:
        task_in_db = await TaskRepository(self.db).get_task_by_id(id=id)

        if isinstance(task_in_db, dict) and not task_in_db.get("id"):
            logger.info("La tarea solicitada no está en base de datos")
            return ServiceResult(TaskExceptions.TaskNotFoundException())

        task = TaskInDB(**task_in_db.dict())
        return ServiceResult(task)

    async def update_task(
        self, id: UUID, task_update: TaskToUpdate, current_user: UserInDB
    ) -> ServiceResult:
        if not is_valid_uuid(id):
            return ServiceResult(TaskExceptions.TaskIdNoValidException())

        try:
            task = await TaskRepository(self.db).update_task(
                id=id,
                task_update=task_update,
                updated_by_id=current_user.id,
            )

            if isinstance(task, dict) and not task.get("id"):
                logger.info("El ID de tarea a actualizar no está en base de datos")
                return ServiceResult(TaskExceptions.TaskNotFoundException())

            return ServiceResult(TaskInDB(**task.dict()))

        except Exception as e:
            logger.error(f"Se produjo un error: {e}")
            return ServiceResult(TaskExceptions.TaskInvalidUpdateParamsException(e))
        
    async def delete_task_by_id(
        self, id: UUID
    ) -> ServiceResult:
        
        task_id = await TaskRepository(self.db).delete_task_by_id(id=id)

        if isinstance(task_id, dict) and not task_id.get("id"):
                logger.info("El ID de tarea a eliminar no está en base de datos")
                return ServiceResult(TaskExceptions.TaskNotFoundException())
        
        return  ServiceResult(task_id)