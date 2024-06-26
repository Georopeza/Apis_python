from typing import List
from uuid import UUID
from pydantic import validator

from shared.utils.schemas_base import BaseSchema, DateTimeModelMixin, IDModelMixin


class TaskBase(BaseSchema):
    task_name: str | None


class TaskCreate(TaskBase):
    task_name: str

    @validator('task_name')
    def task_name_must_have_more_than_three_characters(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError
        return v

class TaskToSave(TaskCreate):
    created_by: UUID | None
    updated_by: UUID | None

class TaskInDB(TaskBase, IDModelMixin, DateTimeModelMixin):
    is_active: bool | None
    created_by: UUID | str | None
    updated_by: UUID | str | None

class TaskToUpdate(TaskBase):
    is_active: bool | None
    