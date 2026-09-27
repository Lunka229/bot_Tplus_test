import chromadb


def get_collection():
    client = chromadb.PersistentClient(
        path="chroma"
    )

    return client.get_or_create_collection(
        name="marketplace_knowledge"
    )