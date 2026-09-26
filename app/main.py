import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from app.bot.handlers.common import (
    create_clear_handler,
    create_message_handler,
    router,
)
from app.config import get_settings
from app.llm.client import OllamaClient
from app.services.conversation import ConversationManager
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

    bot = Bot(
        token=settings.telegram_bot_token,
    )

    ollama_client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )

    llm_service = LLMService(
        client=ollama_client,
    )

    conversation_manager = ConversationManager(
        max_messages=10,
    )

    dp = Dispatcher()
    
    # Регистрируем команду /clear
    router.message.register(
        create_clear_handler(
            conversation_manager,
        ),
        Command("clear"),
    )

    # Регистрируем обработчик обычных текстовых сообщений
    router.message.register(
        create_message_handler(
            llm_service,
            conversation_manager,
        )
    )

    # Подключаем router после регистрации всех handlers
    dp.include_router(router)

    logging.info(
        "Starting Telegram bot | model=%s",
        settings.ollama_model,
    )

    logging.info(
        "Ollama URL: %s",
        settings.ollama_base_url,
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())