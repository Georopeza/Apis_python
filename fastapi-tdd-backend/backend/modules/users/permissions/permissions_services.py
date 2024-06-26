import json

from loguru import logger

from modules.users.permissions import get_permissions
from modules.users.permissions.permissions_exceptions import PermissionsExceptions
from shared.utils.service_result import ServiceResult


class PermissionsService:
    async def list_permissions(self) -> ServiceResult:
        permissions = await get_permissions()

        if not permissions:
            return ServiceResult(PermissionsExceptions.PermissionsListException)

        if len(permissions) == 0:
            return ServiceResult(PermissionsExceptions.PermissionsEmptyListException)

        return ServiceResult(permissions)
