from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.llm.client import OllamaClient


router = Router()


llm_client: OllamaClient | None = None


def set_llm_client(client: OllamaClient) -> None:
    global llm_client
    llm_client = client


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет!\n\n"
        "Я Marketplace AI Bot — помощник продавца "
        "на маркетплейсах.\n\n"
        "Задай мне вопрос о продажах."
    )


@router.message()
async def message_handler(message: Message) -> None:
    if llm_client is None:
        await message.answer(
            "LLM-клиент ещё не настроен."
        )
        return

    user_text = message.text

    if not user_text:
        await message.answer(
            "Пока я умею работать только с текстовыми сообщениями."
        )
        return

    try:
        result = await llm_client.generate(
            prompt=user_text,
            system_prompt=(
                "Ты консультант продавца на маркетплейсах. "
                "Отвечай понятно, кратко и по существу. "
                "Если информации недостаточно, задай уточняющий вопрос."
            ),
        )

        await message.answer(
            f"{result.text}\n\n"
            f"Время: {result.latency_seconds:.2f} сек.\n"
            f"Токены: {result.total_tokens}"
        )

    except Exception:
        await message.answer(
            "Произошла ошибка при обращении к LLM. "
            "Попробуй ещё раз."
        )