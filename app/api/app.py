from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import moderation_router
from app.config.db import close_orm, init_orm


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_orm()
    try:
        yield
    finally:
        await close_orm()


def create_app() -> FastAPI:
    app = FastAPI(title="Travel RT Parser API", version="0.1.0", lifespan=lifespan)
    app.include_router(moderation_router)

    @app.get("/health", tags=["system"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app
