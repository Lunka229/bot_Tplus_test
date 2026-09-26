import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers.common import router
from app.config import get_settings


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def main() -> None:
    settings = get_settings()

    bot = Bot(token=settings.telegram_bot_token)

    dp = Dispatcher()
    dp.include_router(router)

    logging.info("Starting Telegram bot...")
    logging.info("LLM model: %s", settings.ollama_model)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())