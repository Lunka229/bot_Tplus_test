from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.logging import get_logger
from app.llm.exceptions import LLMConnectionError, LLMResponseError
from app.services.conversation import ConversationManager
from app.services.llm_service import LLMService


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

        try:
            request_id, result = await llm_service.generate(
                prompt=message.text,
                history=history[:-1],
                system_prompt=(
                    "Ты консультант продавца "
                    "на маркетплейсах. "
                    "Отвечай понятно, кратко "
                    "и по существу. "
                    "Учитывай контекст предыдущих "
                    "сообщений пользователя. "
                    "Если информации недостаточно, "
                    "задай уточняющий вопрос."
                ),
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