from app.rag.chunker import chunk_text


def test_chunk_text_splits_markdown_sections():
    text = """# Экономика

## Прибыль

Прибыль считается как цена минус себестоимость.

## Маржинальность

Маржинальность считается как прибыль делённая на цену.
"""

    chunks = chunk_text(text)

    assert len(chunks) == 3
    assert "Прибыль" in chunks[1]
    assert "Маржинальность" in chunks[2]


def test_chunk_text_skips_empty_sections():
    text = """# Документ

## Первый раздел

Текст.

## Второй раздел

Текст.
"""

    chunks = chunk_text(text)

    assert len(chunks) == 3