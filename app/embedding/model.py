from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


_model = None


def get_model():
    """
    Embedding modelini yükler.

    Model yalnızca ilk kullanımda yüklenir.
    Sonraki çağrılarda bellekteki mevcut model kullanılır.
    """

    global _model

    if _model is None:
        print("Embedding modeli yükleniyor...")

        _model = SentenceTransformer(MODEL_NAME)

        print("Embedding modeli hazır.")

    return _model


def create_embedding(text: str) -> list[float]:
    """
    Tek bir metin için embedding oluşturur.
    """

    if not text or not text.strip():
        raise ValueError("Embedding için boş metin gönderilemez.")

    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def create_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Birden fazla metin için embedding oluşturur.
    """

    if not texts:
        return []

    model = get_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    return embeddings.tolist()