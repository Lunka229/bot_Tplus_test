from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.logging import get_logger
from app.llm.exceptions import LLMConnectionError, LLMResponseError
from app.services.conversation import ConversationManager
from app.services.llm_service import LLMService

from app.tools.definitions import MARGIN_TOOL

from app.services.router import route_request
from app.services.prompts import PROMPTS

from app.services.rag_service import RAGService

import os
import tempfile

from aiogram import F

from app.services.vision_service import VisionService


router = Router()

logger = get_logger(__name__)


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет!\n\n"
        "Я Marketplace AI Bot — помощник продавца "
        "на маркетплейсах.\n\n"
        "Задай мне вопрос о продажах."
    )


def create_message_handler(
    llm_service: LLMService,
    conversation_manager: ConversationManager,
    rag_service: RAGService,
):
    async def message_handler(message: Message) -> None:
        if not message.text:
            await message.answer(
                "Пока я умею работать только "
                "с текстовыми сообщениями."
            )
            return

        user_id = message.from_user.id

        conversation_manager.add_user_message(
            user_id=user_id,
            content=message.text,
        )

        history = conversation_manager.get_history(
            user_id=user_id
        )

        route = route_request(message.text)

        system_prompt = PROMPTS[route]

        context = await rag_service.build_context(
            query=message.text,
            top_k=3,
        )

        if context:
            system_prompt = (
                f"{system_prompt}\n\n"
                "Используй следующий контекст базы знаний "
                "для ответа на вопрос пользователя.\n"
                "Не выдумывай факты, которых нет в контексте.\n\n"
                f"{context}"
            )

        logger.info(
            "Request routed | user_id=%s | route=%s | rag_context=%s",
            user_id,
            route,
            bool(context),
        )
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        messages.extend(history[:-1])

        messages.append(
            {
                "role": "user",
                "content": message.text,
            }
        )


        
        try:
            mcp_tools = await llm_service.get_mcp_tools()

            all_tools = [
                MARGIN_TOOL,
                *mcp_tools,
            ]

            request_id, result = (
                await llm_service.generate_with_tools(
                    messages=messages,
                    tools=all_tools,
                )
            )

            conversation_manager.add_assistant_message(
                user_id=user_id,
                content=result.text,
            )

            await message.answer(
                f"{result.text}\n\n"
                f"Время: "
                f"{result.latency_seconds:.2f} сек.\n"
                f"Токены: {result.total_tokens}\n"
                f"Request ID: {request_id}"
            )

        except LLMConnectionError:
            logger.exception("LLM connection error")

            await message.answer(
                "Не удалось подключиться к LLM. "
                "Проверь, запущен ли Ollama."
            )

        except LLMResponseError:
            logger.exception("LLM response error")

            await message.answer(
                "LLM вернула некорректный ответ. "
                "Попробуй повторить запрос."
            )

        except Exception:
            logger.exception(
                "Unexpected error while processing message"
            )

            await message.answer(
                "Произошла непредвиденная ошибка. "
                "Попробуй ещё раз."
            )

    return message_handler


def create_clear_handler(
    conversation_manager: ConversationManager,
):
    async def clear_handler(message: Message) -> None:
        user_id = message.from_user.id

        conversation_manager.clear(user_id)

        await message.answer(
            "Контекст диалога очищен."
        )

    return clear_handler

def create_photo_handler(
    vision_service: VisionService,
):
    async def photo_handler(message: Message) -> None:
        if not message.photo:
            return

        request_id = None

        try:
            photo = message.photo[-1]

            bot = message.bot

            with tempfile.NamedTemporaryFile(
                suffix=".jpg",
                delete=False,
            ) as temp_file:
                image_path = temp_file.name

            await bot.download(
                photo,
                destination=image_path,
            )

            prompt = (
                "Ты помощник продавца на маркетплейсе. "
                "Проанализируй изображение товара или "
                "рекламной карточки.\n\n"
                "1. Опиши, что изображено.\n"
                "2. Распознай важный текст на изображении.\n"
                "3. Выдели основные характеристики товара, "
                "если они видны.\n"
                "4. Укажи возможные проблемы или недостатки "
                "визуального оформления.\n"
                "5. Дай несколько практических рекомендаций "
                "продавцу.\n\n"
                "Не придумывай информацию, которой нет "
                "на изображении."
            )

            request_id, result = (
                await vision_service.analyze(
                    image_path=image_path,
                    prompt=prompt,
                )
            )

            await message.answer(
                f"{result.text}\n\n"
                f"Время: "
                f"{result.latency_seconds:.2f} сек.\n"
                f"Токены: {result.total_tokens}\n"
                f"Request ID: {request_id}"
            )

        except LLMConnectionError:
            logger.exception(
                "Vision connection error | request_id=%s",
                request_id,
            )

            await message.answer(
                "Не удалось подключиться к vision-модели. "
                "Проверь, запущен ли Ollama."
            )

        except LLMResponseError:
            logger.exception(
                "Vision response error | request_id=%s",
                request_id,
            )

            await message.answer(
                "Не удалось обработать изображение. "
                "Попробуй отправить его ещё раз."
            )

        except Exception:
            logger.exception(
                "Unexpected vision error | request_id=%s",
                request_id,
            )

            await message.answer(
                "Произошла ошибка при обработке изображения."
            )

        finally:
            if (
                "image_path" in locals()
                and os.path.exists(image_path)
            ):
                os.remove(image_path)

    return photo_handler