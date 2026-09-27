import pytest

from app.bot.handlers.common import create_message_handler
from app.services.conversation import ConversationManager
from app.services.rag_service import RAGService


class FakeRAGService:
    async def build_context(
        self,
        query: str,
        top_k: int = 3,
    ) -> str:
        return (
            "[Источник: economics.md]\n"
            "Маржинальность = Прибыль / Цена продажи × 100%"
        )


class FakeLLMResult:
    text = "Маржинальность рассчитывается как прибыль, делённая на цену продажи."
    latency_seconds = 0.1
    total_tokens = 10


class FakeLLMService:
    def __init__(self):
        self.messages = None
        self.tools = None

    async def generate_with_tools(
        self,
        messages,
        tools,
    ):
        self.messages = messages
        self.tools = tools

        return (
            "test-request-id",
            FakeLLMResult(),
        )


class FakeUser:
    id = 123


class FakeMessage:
    text = "Как рассчитывается маржинальность товара?"
    from_user = FakeUser()

    def __init__(self):
        self.answer_text = None

    async def answer(self, text: str):
        self.answer_text = text


@pytest.mark.anyio
async def test_handler_passes_rag_context_to_llm():
    llm_service = FakeLLMService()
    conversation_manager = ConversationManager()

    handler = create_message_handler(
        llm_service=llm_service,
        conversation_manager=conversation_manager,
        rag_service=FakeRAGService(),
    )

    message = FakeMessage()

    await handler(message)

    assert llm_service.messages is not None

    system_message = llm_service.messages[0]

    assert system_message["role"] == "system"
    assert "economics.md" in system_message["content"]
    assert "Маржинальность = Прибыль / Цена продажи" in (
        system_message["content"]
    )

    assert message.answer_text is not None
