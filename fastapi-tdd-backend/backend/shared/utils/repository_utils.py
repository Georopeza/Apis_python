from datetime import datetime
import pytz
import uuid
from typing import Dict


def preprocess_create(values: Dict) -> Dict:
    if "id" not in values:
        values["id"] = _generate_uuid()
    if "is_active" not in values:
        values["is_active"] = True
    if "created_at" not in values:
        values["created_at"] = _preprocess_date()
    if "updated_at" not in values:
        values["updated_at"] = _preprocess_date()
    return values

def preprocess_update(values: Dict, updated_by: uuid.UUID) -> Dict:
    values["updated_at"] = _preprocess_date()
    values["updated_by"] = updated_by
    return values

def _generate_uuid() -> uuid.UUID:
        return uuid.uuid4()

def _preprocess_date() -> datetime:
    d = datetime.now()
    timezone = pytz.timezone("America/Caracas")
    return timezone.localize(d)