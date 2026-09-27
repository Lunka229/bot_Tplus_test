import pytest

from app.rag.indexer import build_index
from app.rag.retriever import RAGRetriever


@pytest.mark.anyio
async def test_retrieve_economics_document():
    await build_index()

    retriever = RAGRetriever()

    results = await retriever.search(
        "Как рассчитывается маржинальность товара?"
    )

    print("\nRAG RESULTS:")
    for result in results:
        print(
            f"source={result['source']} "
            f"distance={result['distance']}"
        )
        print(result["content"][:300])
        print("---")

    assert results
    assert results[0]["source"] == "economics.md"


@pytest.mark.anyio
async def test_retrieve_product_card_document():
    await build_index()

    retriever = RAGRetriever()

    results = await retriever.search(
        "Как улучшить карточку товара?"
    )

    assert results
    assert results[0]["source"] == "product_cards.md"


@pytest.mark.anyio
async def test_retrieve_marketing_document():
    await build_index()

    retriever = RAGRetriever()

    results = await retriever.search(
        "Как работать с рекламой товара?"
    )

    assert results
    assert results[0]["source"] == "advertising.md"