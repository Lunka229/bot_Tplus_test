import re


def chunk_text(
    text: str,
    max_chars: int = 1000,
) -> list[str]:
    sections = re.split(
        r"\n(?=##\s)",
        text.strip(),
    )

    chunks = []

    for section in sections:
        section = section.strip()

        if not section:
            continue

        if len(section) <= max_chars:
            chunks.append(section)
            continue

        paragraphs = section.split("\n\n")
        current = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            candidate = (
                f"{current}\n\n{paragraph}"
                if current
                else paragraph
            )

            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)

                current = paragraph

        if current:
            chunks.append(current)

    return chunks