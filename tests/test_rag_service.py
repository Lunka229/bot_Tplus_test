import pytest

from app.services.rag_service import RAGService


class FakeRetriever:
    async def search(
        self,
        query: str,
        top_k: int = 3,
    ):
        return [
            {
                "source": "economics.md",
                "content": "Маржинальность = Прибыль / Цена продажи × 100%.",
                "distance": "0.1",
            },
            {
                "source": "economics.md",
                "content": "Прибыль = Цена продажи - Себестоимость.",
                "distance": "0.2",
            },
        ]


@pytest.mark.anyio
async def test_rag_service_builds_context():
    service = RAGService(
        retriever=FakeRetriever()
    )

    context = await service.build_context(
        "Как рассчитывается маржинальность?"
    )

    assert "economics.md" in context
    assert "Маржинальность" in context
    assert "Прибыль" in context