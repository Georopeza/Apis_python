from typing import Dict
from uuid import UUID

from databases import Database
from fastapi import APIRouter, Body, Depends, Path, status
from loguru import logger
from modules.users.auths.auth_dependencies import get_current_active_user
from modules.users.auths.auth_exceptions import AuthExceptions
from modules.users.users.user_schemas import (
    UserActivate,
    UserCreate,
    UserInDB,
    UserOut,
    UserPasswordUpdate,
    UserPublic,
    UserToSave,
    UserUpdate,
)
from modules.users.users.user_services import UserService
from shared.core.db.db_dependencies import get_database
from shared.utils.service_result import ServiceResult, handle_result
from shared.utils.verify_auth import is_authorized

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/",
    response_model=UserOut,
    name="users:create-user",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user: UserCreate = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "users:create-user"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    new_user = UserToSave(**user.dict())
    new_user.created_by = current_user.id
    new_user.updated_by = current_user.id

    result = await UserService(db).create_user(new_user)
    return handle_result(result)


@router.get("/{id}", response_model=UserPublic, name="users:get-user-by-id")
async def get_user_by_id(
    id: UUID = Path(..., title="The id of the user to get"),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "users:get-user-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await UserService(db).get_user_by_id(id=id)
    return handle_result(result)


@router.get("/", response_model=Dict, name="users:users_list", status_code=status.HTTP_200_OK)
async def get_users_list(
    search: str | None = None,
    page_number: int = 1,
    page_size: int = 10,
    order: str = "",
    direction: str = "",
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "users:users_list"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await UserService(db).get_users_list(
        search,
        page_num=page_number,
        page_size=page_size,
        order=order,
        direction=direction,
    )
    return handle_result(result)


@router.put("/{id}", response_model=UserPublic, name="users:update-user-by-id")
async def update_user_by_id(
    id: UUID = Path(..., title="The id of the user to update"),
    user_update: UserUpdate = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "users:update-user-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await UserService(db).update_user(
        id=id, user_update=user_update, current_user=current_user
    )
    return handle_result(result)


@router.put("/activate/{id}", response_model=UserPublic, name="users:activate-user-by-id")
async def activate_user_by_id(
    id: UUID = Path(..., title="The id of the user to update"),
    user_update: UserActivate = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "users:activate-user-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await UserService(db).activate_user(
        id=id, user_update=user_update, current_user=current_user
    )
    return handle_result(result)


@router.delete("/{id}", response_model=UUID, name="users:delete-user-by-id")
async def delete_user_by_id(
    id: UUID = Path(..., title="The id of the user to delete"),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    if not is_authorized(current_user, "users:delete-user-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await UserService(db).delete_user(id=id)
    return handle_result(result)


@router.put("/change_password/{id}", response_model=UserPublic, name="users:change-password-by-id")
async def change_password_by_id(
    id: UUID = Path(..., title="The id of the user to update"),
    psw_update: str = Body(..., embed=True),
    db: Database = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
) -> ServiceResult:
    """
    Un usuario va a poder cambiar su propio password

    Parámetros:
    -**id**: el id del usuario que va a cambiar su password
    -**psw_update**: el nuevo password
    """
    if not is_authorized(current_user, "users:change-password-by-id"):
        return handle_result(ServiceResult(AuthExceptions.AuthUnauthorizedException()))

    result = await UserService(db).change_password_by_id(
        id=id, psw_update=psw_update, current_user=current_user
    )
    return handle_result(result)
