import asyncio
import sys
from dotenv import load_dotenv
from loguru import logger

from app.config.db import close_orm, init_orm
from app.config.settings import settings
from app.models.news import TOPIC_CULTURE, TOPIC_ECOLOGY, TOPIC_SOCIETY
from app.services import IngestionOrchestrator


async def main():
    load_dotenv()
    await init_orm()
    try:
        args = _parse_args(sys.argv[1:])
        orchestrator = IngestionOrchestrator(settings=settings)
        while True:
            result = await orchestrator.run_once(topics=[args["topic"]] if args["topic"] else None)
            _log_result(result)
            if args["once"]:
                break
            await asyncio.sleep(settings.parser_loop_interval_seconds)
    finally:
        await close_orm()


def _parse_args(args: list[str]) -> dict[str, str | bool | None]:
    once = "--once" in args
    raw_topics = [arg for arg in args if not arg.startswith("--")]
    if not raw_topics:
        return {"topic": None, "once": once}
    topic = raw_topics[0].lower().strip()
    allowed = {TOPIC_ECOLOGY, TOPIC_CULTURE, TOPIC_SOCIETY}
    if topic not in allowed:
        raise ValueError(f"Unknown topic: {topic}. Allowed: {', '.join(sorted(allowed))}")
    return {"topic": topic, "once": once}


def _log_result(result: dict) -> None:
    for entity, stats in result.items():
        logger.info(
            "{}: created={}, updated={}, failed={}, skipped={}",
            entity,
            stats.created,
            stats.updated,
            stats.failed,
            stats.skipped,
        )



if __name__ == '__main__':
    asyncio.run(main())
