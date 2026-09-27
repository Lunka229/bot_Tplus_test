from pathlib import Path


KNOWLEDGE_DIR = Path("data/knowledge")


def load_documents() -> list[dict[str, str]]:
    documents = []

    for path in KNOWLEDGE_DIR.glob("*.md"):
        content = path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            continue

        documents.append(
            {
                "source": path.name,
                "content": content,
            }
        )

    return documents