from sys import _current_frames
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from icecream import ic
from modules.users.auths.auth_dependencies import get_current_active_user
from modules.users.auths.auth_exceptions import AuthExceptions
from modules.users.permissions.permissions_schemas import PermissionsOut
from modules.users.permissions.permissions_services import PermissionsService
from modules.users.users.user_schemas import UserInDB
from shared.utils.service_result import ServiceResult, handle_result
from shared.utils.verify_auth import is_authorized

router = APIRouter(
    prefix="/permissions",
    # tags=["permissions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/list", name="permissions:list-permissions")
async def list_permissions(current_user: UserInDB = Depends(get_current_active_user)):
    if not is_authorized(current_user, "permissions:list-permissions"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await PermissionsService().list_permissions()
    return handle_result(result)
