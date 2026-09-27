import pytest

from app.rag.embeddings import OllamaEmbeddings
from app.rag.loader import load_documents


@pytest.mark.anyio
async def test_embedding_similarity():
    embeddings = OllamaEmbeddings()
    documents = load_documents()

    query = "Как рассчитывается маржинальность товара?"
    query_vector = await embeddings.embed(query)

    results = []

    for document in documents:
        vector = await embeddings.embed(document["content"])

        # Косинусное расстояние
        dot = sum(
            a * b
            for a, b in zip(query_vector, vector)
        )

        norm_query = sum(
            a * a
            for a in query_vector
        ) ** 0.5

        norm_vector = sum(
            b * b
            for b in vector
        ) ** 0.5

        similarity = dot / (
            norm_query * norm_vector
        )

        results.append(
            (
                document["source"],
                similarity,
            )
        )

    results.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    print("\nEMBEDDING SIMILARITY:")

    for source, similarity in results:
        print(
            f"{source}: {similarity:.6f}"
        )

    assert results