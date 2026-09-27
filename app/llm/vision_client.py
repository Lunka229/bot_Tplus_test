import base64
import time

import httpx

from app.llm.exceptions import (
    LLMConnectionError,
    LLMResponseError,
)
from app.llm.models import LLMResponse


class VisionClient:
    def __init__(
        self,
        base_url: str,
        model: str = "qwen2.5vl:3b",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
    ) -> LLMResponse:
        try:
            with open(image_path, "rb") as file:
                image_bytes = file.read()
        except OSError as exc:
            raise LLMResponseError(
                f"Cannot read image: {image_path}"
            ) from exc

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64],
                }
            ],
            "stream": False,
        }

        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout
            ) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )

            response.raise_for_status()

        except httpx.ConnectError as exc:
            raise LLMConnectionError(
                f"Cannot connect to Ollama at {self.base_url}"
            ) from exc

        except httpx.HTTPError as exc:
            raise LLMConnectionError(
                "Ollama vision request failed"
            ) from exc

        latency = time.perf_counter() - start_time

        try:
            data = response.json()

            message = data["message"]
            text = message["content"]

            prompt_tokens = int(
                data.get("prompt_eval_count", 0)
            )

            completion_tokens = int(
                data.get("eval_count", 0)
            )

        except (KeyError, TypeError, ValueError) as exc:
            raise LLMResponseError(
                "Invalid vision response from Ollama"
            ) from exc

        total_tokens = (
            prompt_tokens + completion_tokens
        )

        return LLMResponse(
            text=text.strip(),
            latency_seconds=latency,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            model=data.get(
                "model",
                self.model,
            ),
        )