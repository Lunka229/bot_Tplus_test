from app.rag.chunker import chunk_text
from app.rag.embeddings import OllamaEmbeddings
from app.rag.loader import load_documents
from app.rag.vector_store import get_collection


async def build_index() -> int:
    documents = load_documents()

    if not documents:
        raise ValueError(
            "Knowledge base is empty."
        )

    embeddings = OllamaEmbeddings()
    collection = get_collection()

    existing = collection.get()

    if existing["ids"]:
        collection.delete(
            ids=existing["ids"]
        )

    ids = []
    texts = []
    metadatas = []
    vectors = []

    for document in documents:
        source = document["source"]
        content = document["content"]

        chunks = chunk_text(content)

        for chunk_index, chunk in enumerate(chunks):
            vector = await embeddings.embed(chunk)

            ids.append(
                f"{source}:{chunk_index}"
            )
            texts.append(chunk)
            metadatas.append(
                {
                    "source": source,
                    "chunk_index": chunk_index,
                }
            )
            vectors.append(vector)

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=vectors,
    )

    return len(ids)