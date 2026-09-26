import json
from typing import Any

from app.core.logging import get_logger
from app.core.request_context import generate_request_id
from app.llm.client import OllamaClient
from app.llm.models import LLMResponse
from app.tools.executor import execute_tool
from app.tools.validator import validate_tool_arguments


logger = get_logger(__name__)


class LLMService:
    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> tuple[str, LLMResponse]:
        request_id = generate_request_id()

        logger.info(
            "LLM request started | "
            "request_id=%s | model=%s | history_messages=%d",
            request_id,
            self.client.model,
            len(history or []),
        )

        result = await self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            history=history,
        )

        logger.info(
            "LLM request completed | "
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

    async def generate_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> tuple[str, LLMResponse]:
        request_id = generate_request_id()

        logger.info(
            "LLM tool request started | "
            "request_id=%s | model=%s | "
            "messages=%d | tools=%d",
            request_id,
            self.client.model,
            len(messages),
            len(tools),
        )

        total_latency = 0.0
        total_prompt_tokens = 0
        total_completion_tokens = 0

        current_messages = list(messages)

        while True:
            data, latency = await self.client.generate_with_tools(
                messages=current_messages,
                tools=tools,
            )

            total_latency += latency

            total_prompt_tokens += int(
                data.get("prompt_eval_count", 0)
            )

            total_completion_tokens += int(
                data.get("eval_count", 0)
            )

            message = data["message"]

            tool_calls = message.get("tool_calls")

            if not tool_calls:
                text = (
                    message.get("content") or ""
                ).strip()

                result = LLMResponse(
                    text=text,
                    latency_seconds=total_latency,
                    prompt_tokens=total_prompt_tokens,
                    completion_tokens=total_completion_tokens,
                    total_tokens=(
                        total_prompt_tokens
                        + total_completion_tokens
                    ),
                    model=data.get(
                        "model",
                        self.client.model,
                    ),
                )

                logger.info(
                    "LLM tool request completed | "
                    "request_id=%s | latency=%.2f | "
                    "prompt_tokens=%d | "
                    "completion_tokens=%d | "
                    "total_tokens=%d",
                    request_id,
                    result.latency_seconds,
                    result.prompt_tokens,
                    result.completion_tokens,
                    result.total_tokens,
                )

                return request_id, result

            current_messages.append(message)

            for tool_call in tool_calls:
                function = tool_call["function"]

                tool_name = function["name"]

                arguments = function.get(
                    "arguments",
                    {},
                )

                logger.info(
                    "Tool call | "
                    "request_id=%s | "
                    "name=%s | arguments=%s",
                    request_id,
                    tool_name,
                    arguments,
                )

                try:
                    is_valid, validation_error = (
                        validate_tool_arguments(
                            tool_name=tool_name,
                            arguments=arguments,
                            messages=current_messages,
                        )
                    )

                    if not is_valid:
                        logger.warning(
                            "Tool call rejected | "
                            "request_id=%s | "
                            "tool=%s | reason=%s",
                            request_id,
                            tool_name,
                            validation_error,
                        )

                        tool_result = json.dumps(
                            {
                                "error": "tool_call_rejected",
                                "message": (
                                    "Нельзя использовать "
                                    "неподтверждённые данные. "
                                    "Попроси пользователя "
                                    "указать недостающие данные."
                                ),
                                "details": validation_error,
                            },
                            ensure_ascii=False,
                        )

                    else:
                        tool_result = execute_tool(
                            tool_name=tool_name,
                            arguments=arguments,
                        )

                except Exception as exc:
                    logger.exception(
                        "Tool execution failed | "
                        "request_id=%s | tool=%s",
                        request_id,
                        tool_name,
                    )

                    tool_result = json.dumps(
                        {
                            "error": str(exc),
                        },
                        ensure_ascii=False,
                    )

                logger.info(
                    "Tool result | "
                    "request_id=%s | "
                    "tool=%s | result=%s",
                    request_id,
                    tool_name,
                    tool_result,
                )

                current_messages.append(
                    {
                        "role": "tool",
                        "content": tool_result,
                        "tool_name": tool_name,
                    }
                )