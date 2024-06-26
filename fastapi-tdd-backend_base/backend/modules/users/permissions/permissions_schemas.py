from typing import List, Dict

from shared.utils.schemas_base import BaseSchema, IDModelMixin


class PermissionsBase(BaseSchema):
    """
    Common charcateristics of permissions
    """

    functionality: str | None
    routes: List | None


class PermissionsOut(PermissionsBase):
    pass
