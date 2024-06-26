from typing import Dict
from urllib import response
from uuid import UUID

from databases import Database
from fastapi import APIRouter, Body, Depends, Path, status
from loguru import logger
from modules.users.auths.auth_dependencies import get_current_active_user
from modules.users.auths.auth_exceptions import AuthExceptions
from modules.users.roles.role_schemas import (
    RoleCreate,
    RoleIn,
    RoleOut,
    RoleUpdate,
    RoleUpdateActive,
)
from modules.users.roles.role_services import RoleService
from modules.users.users.user_schemas import UserInDB
from pydantic.error_wrappers import ValidationError
from shared.core.db.db_dependencies import get_database
from shared.utils.service_result import ServiceResult, handle_result
from shared.utils.verify_auth import is_authorized

router = APIRouter(
    prefix="/roles",
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=RoleOut,
    name="roles:create-role",
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    role: RoleCreate = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "roles:create-role"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    new_role = RoleIn(**role.dict())
    new_role.created_by = current_user.id
    new_role.updated_by = current_user.id
    result = await RoleService().create_role(new_role, db)
    return handle_result(result)


@router.get("/", response_model=Dict, name="roles:roles_list", status_code=status.HTTP_200_OK)
async def get_roles_list(
    search: str | None = None,
    page_number: int = 1,
    page_size: int = 10,
    order: str = "",
    direction: str = "",
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "roles:roles_list"):
        return ServiceResult(AuthExceptions.AuthUnauthorizedException())

    result = await RoleService().get_roles_list(
        db=db,
        search=search,
        page_num=page_number,
        page_size=page_size,
        order=order,
        direction=direction,
    )
    return handle_result(result)


@router.get("/{id}/", response_model=RoleOut, name="roles:get-role-by-id")
async def get_role_by_id(
    id: UUID,
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "roles:get-role-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await RoleService().get_role_by_id(db=db, id=id)
    return handle_result(result)


@router.put("/{id}", response_model=RoleOut, name="roles:update-role-by-id")
async def update_role_by_id(
    id: UUID = Path(..., title="The id of the role to update"),
    role_update: RoleUpdate = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "roles:update-role-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await RoleService().update_role(
        db=db, id=id, role_update=role_update, current_user=current_user
    )
    return handle_result(result)


@router.put("/activate/{id}", response_model=RoleOut, name="roles:update-activate-role-by-id")
async def update_activate_role_by_id(
    id: UUID = Path(..., title="The id of the role to update is_active"),
    role_update: RoleUpdateActive = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "roles:update-activate-role-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await RoleService().update_activate_role(
        db=db, id=id, role_update=role_update, current_user=current_user
    )
    return handle_result(result)


@router.delete("/{id}", response_model=UUID, name="roles:delete-role-by-id")
async def delete_role_by_id(
    id: UUID = Path(..., title="The id of the role to update is_active"),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, endpoint="roles:delete-role-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await RoleService().delete_role(db=db, id=id)
    return handle_result(result)
