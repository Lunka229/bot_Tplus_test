from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет!\n\n"
        "Я Marketplace AI Bot — помощник продавца "
        "на маркетплейсах.\n\n"
        "Пока я нахожусь в разработке."
    )


@router.message()
async def message_handler(message: Message) -> None:
    await message.answer(
        "Я получил твоё сообщение.\n"
        "Подключение LLM добавим на следующем этапе."
    )