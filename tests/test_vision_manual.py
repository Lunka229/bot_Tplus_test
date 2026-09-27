import asyncio

from app.config import get_settings
from app.llm.vision_client import VisionClient


async def main() -> None:
    settings = get_settings()

    client = VisionClient(
        base_url=settings.ollama_base_url,
        model="qwen2.5vl:3b",
    )

    result = await client.analyze_image(
        image_path="tests/fixtures/test_image.png",
        prompt=(
            "Проанализируй изображение. "
            "Опиши, что на нём изображено, "
            "и отдельно перечисли весь текст, "
            "который удалось распознать."
        ),
    )

    print("\n=== VISION RESULT ===")
    print(result.text)
    print("\n=== METRICS ===")
    print(f"Model: {result.model}")
    print(f"Latency: {result.latency_seconds:.2f} sec")
    print(f"Prompt tokens: {result.prompt_tokens}")
    print(f"Completion tokens: {result.completion_tokens}")
    print(f"Total tokens: {result.total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())