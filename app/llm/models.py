from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    text: str
    latency_seconds: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str