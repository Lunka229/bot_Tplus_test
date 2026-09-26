from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.logging import get_logger
from app.llm.exceptions import LLMConnectionError, LLMResponseError
from app.services.llm_service import LLMService


router = Router()
logger = get_logger(__name__)


@router.message(CommandStart())
async def start_handler(
    message: Message,
) -> None:
    await message.answer(
        "Привет!\n\n"
        "Я Marketplace AI Bot — помощник продавца "
        "на маркетплейсах.\n\n"
        "Задай мне вопрос о продажах."
    )


def create_message_handler(
    llm_service: LLMService,
):
    async def message_handler(
        message: Message,
    ) -> None:
        if not message.text:
            await message.answer(
                "Пока я умею работать только "
                "с текстовыми сообщениями."
            )
            return

        try:
            request_id, result = await llm_service.generate(
                prompt=message.text,
                system_prompt=(
                    "Ты консультант продавца "
                    "на маркетплейсах. "
                    "Отвечай понятно, кратко "
                    "и по существу. "
                    "Если информации недостаточно, "
                    "задай уточняющий вопрос."
                ),
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

    return message_handler