from databases import Database
from loguru import logger
from typing import List
from uuid import UUID

from modules.tasks.task_exceptions import TaskExceptions
from modules.tasks.task_schemas import (
    TaskToSave, 
    TaskInDB,
    TaskToUpdate
)
from shared.utils.record_to_dict import record_to_dict
import shared.utils.repository_utils as ru

class TaskRepository:
    def __init__(self, db: Database):
        self.db = db

    async def create_task(self, task: TaskToSave) -> TaskInDB:
        from modules.tasks.task_sqlstaments import CREATE_TASK_ITEM

        values = ru.preprocess_create(task.dict())
        record = await self.db.fetch_one(query=CREATE_TASK_ITEM, values=values)

        result = record_to_dict(record)

        return TaskInDB(**result)

    async def get_tasks_list(
        self,
        search: str | None,
        order: str | None,
        direction: str | None,
    ) -> List:
        from modules.tasks.task_sqlstaments import (
            GET_TASKS_LIST,
            task_list_complements,
            task_list_search,
        )

        order = order.lower() if order != None else None
        direction = direction.upper() if order != None else None
        values = {}
        sql_sentence = task_list_complements(order, direction)
        sql_search = task_list_search()

        if not search:
            sql_sentence = GET_TASKS_LIST + sql_sentence
        else:
            sql_sentence = GET_TASKS_LIST + sql_search + sql_sentence
            values["search"] = "%" + search + "%"

        records = await self.db.fetch_all(query=sql_sentence, values=values)

        if len(records) == 0 or not records:
            return []
        
        return [TaskInDB(**dict(record)) for record in records] 


    async def get_task_by_id(self, id: UUID) -> TaskInDB | dict:
        from modules.tasks.task_sqlstaments import GET_TASK_BY_ID

        values = {"id": id}
        record = await self.db.fetch_one(query=GET_TASK_BY_ID, values=values)
        if not record:
            return {}

        task = record_to_dict(record)
        return TaskInDB(**task)
    
    async def update_task(
        self,
        id: UUID,
        task_update: TaskToUpdate,
        updated_by_id: UUID,
    ) -> TaskInDB | dict:
        from modules.tasks.task_sqlstaments import UPDATE_TASK_BY_ID

        task = await self.get_task_by_id(id=id)
        if not task:
            return {}

        task_update_params = task.copy(update=task_update.dict(exclude_unset=True))

        task_params_dict = task_update_params.dict()
        task_params_dict["updated_by"] = updated_by_id
        task_params_dict["updated_at"] = ru._preprocess_date()
        
        try:
            record = await self.db.fetch_one(query=UPDATE_TASK_BY_ID, values=task_params_dict)
            task_updated = record_to_dict(record)
            return await self.get_task_by_id(id=task_updated.get("id"))
        except Exception as e:
            logger.error(f"Datos inválidos para actualizar una tarea: {e}")
            raise TaskExceptions.TaskInvalidUpdateParamsException()
        
    async def delete_task_by_id(
        self,
        id: UUID,
    ) -> UUID | dict:
        from modules.tasks.task_sqlstaments import DELETE_TASK_BY_ID

        task = await self.get_task_by_id(id=id)

        if not task:
            return {}
        
        record = await self.db.fetch_one(query= DELETE_TASK_BY_ID, values = {"id": id})
        task_id_delete = dict(record)        

        return task_id_delete