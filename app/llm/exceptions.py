class LLMError(Exception):
    """Base exception for LLM-related errors."""


class LLMConnectionError(LLMError):
    """Raised when the LLM service cannot be reached."""


class LLMResponseError(LLMError):
    """Raised when the LLM returns an invalid response."""