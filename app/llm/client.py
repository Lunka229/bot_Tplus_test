import time

import httpx

from app.llm.exceptions import LLMConnectionError, LLMResponseError
from app.llm.models import LLMResponse
from typing import Any

class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], float]:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
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
                "Ollama HTTP request failed"
            ) from exc

        latency = time.perf_counter() - start_time

        try:
            data = response.json()

        except ValueError as exc:
            raise LLMResponseError(
                "Invalid JSON response from Ollama"
            ) from exc

        return data, latency

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> LLMResponse:
        messages: list[dict[str, str]] = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        if history:
            messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        payload = {
            "model": self.model,
            "messages": messages,
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
                "Ollama HTTP request failed"
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
                "Invalid response received from Ollama"
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
            model=data.get("model", self.model),
        )