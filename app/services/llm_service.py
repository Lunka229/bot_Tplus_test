from app.core.logging import get_logger
from app.core.request_context import generate_request_id
from app.llm.client import OllamaClient
from app.llm.models import LLMResponse


logger = get_logger(__name__)


class LLMService:
    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> tuple[str, LLMResponse]:
        request_id = generate_request_id()

        logger.info(
            "LLM request started | request_id=%s | model=%s",
            request_id,
            self.client.model,
        )

        result = await self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        logger.info(
            "LLM request completed | "
            "request_id=%s | latency=%.2f | "
            "tokens=%d",
            request_id,
            result.latency_seconds,
            result.total_tokens,
        )

        return request_id, result