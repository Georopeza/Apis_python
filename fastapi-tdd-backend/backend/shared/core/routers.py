from fastapi import APIRouter
from modules.users import users_router
from modules.tasks.task_routes import task_router


router = APIRouter()

router.include_router(users_router)
router.include_router(task_router)

