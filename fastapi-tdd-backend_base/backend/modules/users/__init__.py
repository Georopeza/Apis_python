from fastapi import APIRouter

from modules.users.auths.auth_routes import router as auth_router
from modules.users.permissions.permissions_routes import router as permissions_router
from modules.users.roles.role_routes import router as roles_router
from modules.users.users.user_routes import router as user_router

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

users_router.include_router(auth_router)
users_router.include_router(permissions_router)
users_router.include_router(roles_router)
users_router.include_router(user_router)
