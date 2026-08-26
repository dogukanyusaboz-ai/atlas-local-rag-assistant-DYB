from typing import List


def clean_text(text: str) -> str:
    """
    Metindeki gereksiz boşlukları temizler.
    """
    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def create_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> List[str]:
    """
    Metni belirli boyutlarda parçalara böler.

    chunk_size:
        Her chunk'ın yaklaşık karakter uzunluğu.

    overlap:
        Bir önceki chunk'ın sonunda bulunan ve
        sonraki chunk'a tekrar dahil edilen karakter sayısı.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size 0'dan büyük olmalıdır.")

    if overlap < 0:
        raise ValueError("overlap negatif olamaz.")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap, chunk_size değerinden küçük olmalıdır."
        )

    text = clean_text(text)

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks