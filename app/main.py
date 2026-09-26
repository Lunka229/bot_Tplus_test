import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers.common import (
    create_message_handler,
    router,
)
from app.config import get_settings
from app.llm.client import OllamaClient
from app.services.llm_service import LLMService


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)


async def main() -> None:
    settings = get_settings()

    bot = Bot(token=settings.telegram_bot_token)

    ollama_client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )

    llm_service = LLMService(
        client=ollama_client,
    )

    dp = Dispatcher()

    dp.include_router(router)

    dp.message.register(
        create_message_handler(llm_service)
    )

    logging.info(
        "Starting Telegram bot | model=%s",
        settings.ollama_model,
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())