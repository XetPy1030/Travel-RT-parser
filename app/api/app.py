from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.auth import get_current_user
from app.api.routers import auth_router, moderation_router
from app.config.db import close_orm, init_orm
from app.config.settings import settings
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_orm()
    try:
        yield
    finally:
        await close_orm()


def create_app() -> FastAPI:
    app = FastAPI(title="Travel RT Parser API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(moderation_router, dependencies=[Depends(get_current_user)])

    @app.get("/health", tags=["system"], response_model=HealthResponse)
    async def healthcheck() -> HealthResponse:
        return HealthResponse(status="ok")

    return app
