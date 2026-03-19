import asyncio
import sys

from dotenv import load_dotenv
from loguru import logger

from app.config.db import close_orm, init_orm
from app.config.settings import settings
from app.services.backend_sync_service import BackendSyncService


async def main() -> None:
    load_dotenv()
    await init_orm()
    try:
        # from app.models import News
        # await News.filter(moderation_status=News.MODERATION_APPROVED).update(needs_backend_update=True)
        # n = await News.last()
        # print(n.parsed_title)
        # n.needs_backend_update = True
        # await n.save()

        once = "--once" in sys.argv[1:]
        service = BackendSyncService(settings=settings)
        while True:
            stats = await service.sync_approved_news()
            logger.info("Sender: sent={}, failed={}, skipped={}", stats.sent, stats.failed, stats.skipped)
            if once:
                break
            await asyncio.sleep(settings.sender_loop_interval_seconds)
    finally:
        await close_orm()


if __name__ == "__main__":
    asyncio.run(main())
