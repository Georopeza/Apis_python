import abc
import uuid
from datetime import datetime
from typing import Dict, List, Mapping

import pytz
import sqlalchemy
from databases import Database
from fastapi import FastAPI
from loguru import logger
from modules.users.users.user_schemas import UserInDB
from shared.core.db.db_base import database
from shared.utils.schemas_base import BaseSchema


class BaseRepository(abc.ABC):
    def __init__(self, db: Database, *args, **kwargs) -> None:
        self.db = db
        super()

    @property
    @abc.abstractmethod
    def _schema_out(self):
        pass

    @property
    @abc.abstractmethod
    def _schema_in(self):
        pass

    @staticmethod
    def generate_uuid() -> uuid.UUID:
        return uuid.uuid4()

    def preprocess_create(self, values: Dict) -> Dict:
        if "id" not in values:
            values["id"] = self.generate_uuid()
        if "is_active" not in values:
            values["is_active"] = True
        if "created_at" not in values:
            values["created_at"] = self._preprocess_date()
        if "updated_at" not in values:
            values["updated_at"] = self._preprocess_date()
        return values

    def preprocess_update(self, values: Dict, updated_by: uuid.UUID) -> Dict:
        values["updated_at"] = self._preprocess_date()
        values["updated_by"] = updated_by
        return values

    def _preprocess_date(self) -> datetime:
        d = datetime.now()
        timezone = pytz.timezone("America/Caracas")
        return timezone.localize(d)
