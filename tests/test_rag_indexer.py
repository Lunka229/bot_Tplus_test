import pytest

from app.rag.indexer import build_index
from app.rag.vector_store import get_collection


@pytest.mark.anyio
async def test_build_rag_index():
    count = await build_index()

    assert count >= 4

    collection = get_collection()

    result = collection.get()

    assert len(result["ids"]) == count
    assert len(result["documents"]) == count
    assert len(result["metadatas"]) == count


@pytest.mark.anyio
async def test_rag_documents_have_sources():
    await build_index()

    collection = get_collection()

    result = collection.get()

    sources = {
        metadata["source"]
        for metadata in result["metadatas"]
    }

    assert "economics.md" in sources
    assert "advertising.md" in sources
    assert "product_cards.md" in sources
    assert "support.md" in sources