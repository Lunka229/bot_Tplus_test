import asyncio

from app.rag.indexer import build_index


async def main():
    count = await build_index()

    print(
        f"RAG index built successfully. "
        f"Documents: {count}"
    )


if __name__ == "__main__":
    asyncio.run(main())