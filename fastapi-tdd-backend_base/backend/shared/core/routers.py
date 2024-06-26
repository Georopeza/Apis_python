from fastapi import APIRouter
from modules.users import users_router

router = APIRouter()

router.include_router(users_router)
