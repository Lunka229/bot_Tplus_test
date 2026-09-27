import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from app.bot.handlers.common import (
    create_clear_handler,
    create_message_handler,
    create_photo_handler,
    router,
)
from app.config import get_settings
from app.llm.client import OllamaClient
from app.services.conversation import ConversationManager
from app.services.llm_service import LLMService

from app.services.rag_service import RAGService
from app.rag.indexer import build_index

from app.llm.vision_client import VisionClient
from app.services.vision_service import VisionService

from aiogram import Bot, Dispatcher, F

from app.mcp.client import MCPClient


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
    vision_client = VisionClient(
        base_url=settings.ollama_base_url,
        model="qwen2.5vl:3b",
    )
    vision_service = VisionService(
        client=vision_client,
    )
    
    mcp_client = MCPClient()

    llm_service = LLMService(
        client=ollama_client,
        mcp_client=mcp_client,
    )

    conversation_manager = ConversationManager(
        max_messages=10,
    )
    rag_service = RAGService()

    dp = Dispatcher()

    router.message.register(
        create_photo_handler(
            vision_service,
        ),
        F.photo,
    )     

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
            rag_service,
        )
    )   

    dp.include_router(router)

    logging.info(
        "Starting Telegram bot | model=%s",
        settings.ollama_model,
    )

    logging.info(
        "Ollama URL: %s",
        settings.ollama_base_url,
    )
    logging.info(
        "Building RAG index..."
    )

    await build_index()

    logging.info(
        "RAG index built successfully"
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())