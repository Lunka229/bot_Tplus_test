from app.rag.embeddings import OllamaEmbeddings
from app.rag.vector_store import get_collection


class RAGRetriever:
    def __init__(
        self,
        embeddings: OllamaEmbeddings | None = None,
    ) -> None:
        self.embeddings = (
            embeddings
            or OllamaEmbeddings()
        )

    async def search(
        self,
        query: str,
        top_k: int = 2,
    ) -> list[dict[str, str]]:
        collection = get_collection()

        query_vector = await self.embeddings.embed(
            query
        )

        result = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        results = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):
            results.append(
                {
                    "content": document,
                    "source": metadata["source"],
                    "distance": str(distance),
                }
            )

        return results