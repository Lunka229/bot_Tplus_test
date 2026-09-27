from app.core.request_context import generate_request_id
from app.core.logging import get_logger
from app.llm.models import LLMResponse
from app.llm.vision_client import VisionClient


logger = get_logger(__name__)


class VisionService:
    def __init__(
        self,
        client: VisionClient,
    ) -> None:
        self.client = client

    async def analyze(
        self,
        image_path: str,
        prompt: str,
    ) -> tuple[str, LLMResponse]:
        request_id = generate_request_id()

        logger.info(
            "Vision request started | "
            "request_id=%s | model=%s | image=%s",
            request_id,
            self.client.model,
            image_path,
        )

        result = await self.client.analyze_image(
            image_path=image_path,
            prompt=prompt,
        )

        logger.info(
            "Vision request completed | "
            "request_id=%s | latency=%.2f | "
            "prompt_tokens=%d | completion_tokens=%d | "
            "total_tokens=%d",
            request_id,
            result.latency_seconds,
            result.prompt_tokens,
            result.completion_tokens,
            result.total_tokens,
        )

        return request_id, result