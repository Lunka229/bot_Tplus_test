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

from app.bot.keyboards.main import get_main_keyboard
from aiogram.fsm.context import FSMContext

from app.bot.states import MarginStates
from app.bot.keyboards.main import get_main_keyboard



router = Router()

logger = get_logger(__name__)



@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет!\n\n"
        "Я Marketplace AI Bot — помощник продавца "
        "на маркетплейсах.\n\n"
        "Задай мне вопрос или выбери действие:",
        reply_markup=get_main_keyboard(),
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
    async def clear_handler(
        message: Message,
        state: FSMContext,
    ) -> None:
        user_id = message.from_user.id

        conversation_manager.clear(user_id)

        await state.clear()

        await message.answer(
            "Контекст диалога очищен.",
            reply_markup=get_main_keyboard(),
        )

    return clear_handler


def create_margin_handler(
    llm_service: LLMService,
):
    async def margin_start_handler(
        message: Message,
        state: FSMContext,
    ) -> None:
        await state.set_state(
            MarginStates.waiting_for_price
        )

        await message.answer(
            "Введите цену продажи товара в рублях:"
        )

    async def margin_price_handler(
        message: Message,
        state: FSMContext,
    ) -> None:
        if not message.text:
            await message.answer(
                "Введите цену числом.\n"
                "Например: 1000"
            )
            return

        try:
            price = float(
                message.text.replace(",", ".").strip()
            )

            if price <= 0:
                raise ValueError

        except ValueError:
            await message.answer(
                "Некорректная цена.\n"
                "Введите положительное число, например: 1000"
            )
            return

        await state.update_data(
            price=price
        )

        await state.set_state(
            MarginStates.waiting_for_cost
        )

        await message.answer(
            "Теперь введите себестоимость товара в рублях:"
        )

    async def margin_cost_handler(
        message: Message,
        state: FSMContext,
    ) -> None:
        if not message.text:
            await message.answer(
                "Введите себестоимость числом.\n"
                "Например: 600"
            )
            return

        try:
            cost = float(
                message.text.replace(",", ".").strip()
            )

            if cost <= 0:
                raise ValueError

        except ValueError:
            await message.answer(
                "Некорректная себестоимость.\n"
                "Введите положительное число, например: 600"
            )
            return

        data = await state.get_data()

        price = data.get("price")

        if price is None:
            await state.clear()

            await message.answer(
                "Не удалось получить цену. "
                "Начните расчёт заново."
            )
            return

        if cost > price:
            await message.answer(
                "Себестоимость не должна быть больше "
                "цены продажи.\n\n"
                f"Цена продажи: {price:.2f} ₽\n"
                f"Себестоимость: {cost:.2f} ₽\n\n"
                "Введите себестоимость ещё раз:"
            )
            return

        try:
            tool_result = await llm_service.call_mcp_tool(
                tool_name="calculate_margin_tool",
                arguments={
                    "price": price,
                    "cost": cost,
                },
            )

            logger.info(
                "MCP margin button call | "
                "price=%s | cost=%s | result=%s",
                price,
                cost,
                tool_result,
            )

            import json

            result_data = json.loads(tool_result)

            profit = result_data.get(
                "profit",
                0,
            )

            margin_percent = result_data.get(
                "margin_percent",
                0,
            )

            markup_percent = result_data.get(
                "markup_percent",
                0,
            )

            await message.answer(
                "🧮 Результат расчёта\n\n"
                f"Цена продажи: {price:.2f} ₽\n"
                f"Себестоимость: {cost:.2f} ₽\n"
                f"Прибыль: {profit:.2f} ₽\n"
                f"Маржинальность: {margin_percent:.2f}%\n"
                f"Наценка: {markup_percent:.2f}%",
                reply_markup=get_main_keyboard(),
            )

        except Exception:
            logger.exception(
                "MCP margin button error"
            )

            await message.answer(
                "Не удалось выполнить расчёт через MCP. "
                "Попробуйте ещё раз."
            )

        finally:
            await state.clear()

    router.message.register(
        margin_start_handler,
        F.text == "🧮 Рассчитать маржу",
    )

    router.message.register(
        margin_price_handler,
        MarginStates.waiting_for_price,
    )

    router.message.register(
        margin_cost_handler,
        MarginStates.waiting_for_cost,
    )

    return margin_start_handler

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