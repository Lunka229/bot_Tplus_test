import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.bot.handlers.common import router, set_llm_client
from app.config import get_settings
from app.llm.client import OllamaClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)


async def main() -> None:
    settings = get_settings()

    bot = Bot(token=settings.telegram_bot_token)

    llm_client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )

    set_llm_client(llm_client)

    dp = Dispatcher()
    dp.include_router(router)

    logging.info("Starting Telegram bot...")
    logging.info("LLM model: %s", settings.ollama_model)
    logging.info("Ollama URL: %s", settings.ollama_base_url)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())