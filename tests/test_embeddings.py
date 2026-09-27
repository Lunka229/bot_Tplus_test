import pytest

from app.rag.embeddings import OllamaEmbeddings


@pytest.mark.anyio
async def test_embedding_generation():
    embeddings = OllamaEmbeddings()

    vector = await embeddings.embed(
        "Как рассчитывается маржинальность товара?"
    )

    assert vector
    assert isinstance(vector, list)
    assert len(vector) > 100