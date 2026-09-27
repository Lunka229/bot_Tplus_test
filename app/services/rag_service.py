from app.rag.retriever import RAGRetriever


class RAGService:
    def __init__(
        self,
        retriever: RAGRetriever | None = None,
    ) -> None:
        self.retriever = retriever or RAGRetriever()

    async def build_context(
        self,
        query: str,
        top_k: int = 3,
    ) -> str:
        results = await self.retriever.search(
            query=query,
            top_k=top_k,
        )

        if not results:
            return ""

        chunks = []

        for result in results:
            chunks.append(
                f"[Источник: {result['source']}]\n"
                f"{result['content']}"
            )

        return "\n\n---\n\n".join(chunks)