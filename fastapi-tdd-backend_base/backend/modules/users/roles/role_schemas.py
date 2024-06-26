from typing import List
from uuid import UUID

from shared.utils.schemas_base import BaseSchema, IDModelMixin, DateTimeModelMixin


class RoleBase(BaseSchema):
    """
    Common charcateristics of permissions
    """

    role: str | None
    permissions: List[str] | None


class RoleIn(RoleBase):
    role: str
    permissions: List[str]
    created_by: UUID | None
    updated_by: UUID | None


class RoleCreate(RoleBase):
    role: str
    permissions: List[str]


class RoleUpdate(RoleBase):
    pass


class RoleOut(RoleBase, IDModelMixin, DateTimeModelMixin):
    created_by: str | None
    updated_by: str | None
    is_active: bool | None


class RoleUpdateActive(BaseSchema):
    is_active: bool | None
