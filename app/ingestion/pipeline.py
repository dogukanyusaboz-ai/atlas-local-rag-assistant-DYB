from pathlib import Path
from datetime import datetime
import json

from app.ingestion.loaders import load_document
from app.ingestion.chunker import create_chunks
from app.embedding.model import create_embeddings

from app.database.repository import (
    save_document,
    save_chunk_with_embedding,
    document_exists,
)


def ingest_file(
    file_path: str,
    chunk_size: int = 1000,
    overlap: int = 150,
):
    """
    Belgeyi okur, chunk'lara böler,
    embedding oluşturur ve veritabanına kaydeder.
    """

    path = Path(file_path)

    # Dosya var mı?
    if not path.exists():
        raise FileNotFoundError(
            f"Dosya bulunamadı: {file_path}"
        )

    # Daha önce eklenmiş mi?
    if document_exists(path.name):
        print(
            f"Belge zaten database'de mevcut: {path.name}"
        )

        return {
            "document_id": None,
            "filename": path.name,
            "file_type": path.suffix.lower(),
            "text_length": 0,
            "chunks": [],
            "already_exists": True,
        }

    print(f"Belge okunuyor: {path.name}")

    # Belgeyi oku
    text = load_document(str(path))

    if not text.strip():
        raise ValueError(
            f"Belgede okunabilir metin bulunamadı: {path.name}"
        )

    print(f"Metin uzunluğu: {len(text)} karakter")

    # Chunk oluştur
    chunks = create_chunks(
        text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    print(f"Oluşturulan chunk sayısı: {len(chunks)}")

    # Tüm chunk'ların embedding'lerini tek seferde oluştur
    print("Embedding'ler oluşturuluyor...")

    embeddings = create_embeddings(chunks)

    print("Embedding'ler hazır.")

    # Belgeyi database'e kaydet
    document_id = save_document(
        filename=path.name,
        file_type=path.suffix.lower(),
        created_at=datetime.now().isoformat(),
    )

    print(
        f"Belge database'e kaydedildi. ID: {document_id}"
    )

    # Chunk + embedding kayıtları
    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        embedding_json = json.dumps(embedding)

        save_chunk_with_embedding(
            document_id=document_id,
            chunk_index=index,
            content=chunk,
            embedding=embedding_json,
        )

    print(
        f"{len(chunks)} chunk ve embedding database'e kaydedildi."
    )

    return {
        "document_id": document_id,
        "filename": path.name,
        "file_type": path.suffix.lower(),
        "text_length": len(text),
        "chunks": chunks,
        "already_exists": False,
    }