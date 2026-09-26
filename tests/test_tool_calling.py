import pytest

from app.config import get_settings
from app.llm.client import OllamaClient
from app.services.llm_service import LLMService
from app.tools.definitions import MARGIN_TOOL


@pytest.mark.anyio
async def test_margin_tool_calling():
    settings = get_settings()

    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )

    service = LLMService(
        client=client,
    )

    messages = [
        {
            "role": "system",
            "content": (
                "Ты консультант продавца "
                "на маркетплейсах. "
                "Если пользователь просит "
                "рассчитать маржинальность, "
                "используй calculate_margin."
            ),
        },
        {
            "role": "user",
            "content": (
                "Цена товара 1500 рублей, "
                "себестоимость 600 рублей. "
                "Какая маржинальность?"
            ),
        },
    ]

    request_id, result = await service.generate_with_tools(
        messages=messages,
        tools=[MARGIN_TOOL],
    )

    assert request_id
    assert result.text
    assert "60" in result.text
    assert result.total_tokens > 0