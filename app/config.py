from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    ollama_model: str
    ollama_base_url: str


def get_settings() -> Settings:
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not telegram_bot_token:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is not set in the environment."
        )

    return Settings(
        telegram_bot_token=telegram_bot_token,
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        ollama_base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        ),
    )