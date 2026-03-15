from app.config.settings import settings
from tortoise import Tortoise


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.postgres_host,
                "port": settings.postgres_port,
                "user": settings.postgres_user,
                "password": settings.postgres_password,
                "database": settings.postgres_db,
            },
        },
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
            "migrations": "app.migrations",
        },
    },
}


async def init_orm() -> None:
    await Tortoise.init(config=TORTOISE_ORM)


async def close_orm() -> None:
    await Tortoise.close_connections()
