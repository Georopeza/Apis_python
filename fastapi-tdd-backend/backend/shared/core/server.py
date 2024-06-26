import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from shared.core import config
from shared.core.handlers import create_start_app_handler, create_stop_app_handler
from shared.core.routers import router
from shared.utils.app_exceptions import AppExceptionCase, app_exception_handler


def get_application():
    app = FastAPI(
        title=config.PROJECT_NAME,
        description=config.DESCRIPTION,
        version=config.VERSION,
        debug=config.DEBUG,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_event_handler("startup", create_start_app_handler(app))
    app.add_event_handler("shutdown", create_stop_app_handler(app))

    @app.exception_handler(AppExceptionCase)
    async def custom_app_exception_handler(request, e):
        return await app_exception_handler(request, e)

    app.include_router(router, prefix=config.API_PREFIX)

    @app.get("/")
    def home():
        return {"message": "Bienvenido al backend del Sistema Demo de Desarrollo de APIs con Python"}

    return app


app = get_application()
