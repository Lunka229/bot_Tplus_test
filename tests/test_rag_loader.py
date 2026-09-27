from app.rag.loader import load_documents


def test_load_knowledge_documents():
    documents = load_documents()

    assert documents

    sources = {
        document["source"]
        for document in documents
    }

    assert "economics.md" in sources
    assert "advertising.md" in sources
    assert "product_cards.md" in sources
    assert "support.md" in sources


def test_documents_have_content():
    documents = load_documents()

    for document in documents:
        assert document["source"]
        assert document["content"]
        assert len(document["content"]) > 50