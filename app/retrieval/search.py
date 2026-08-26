import sqlite3
import json
from pathlib import Path

import numpy as np

from app.core.config import DATABASE_PATH
from app.embedding.model import create_embedding


def search_documents(
    query: str,
    top_k: int = 5,
    min_similarity: float = 0.25,
):
    """
    Kullanıcının sorusuna en benzer belge chunk'larını bulur.
    """

    # Soru embedding'i
    query_embedding = np.array(
        create_embedding(query),
        dtype=np.float32,
    )

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            chunks.id,
            chunks.document_id,
            chunks.chunk_index,
            chunks.content,
            chunks.embedding,
            documents.filename
        FROM chunks
        JOIN documents
            ON chunks.document_id = documents.id
        WHERE chunks.embedding IS NOT NULL
        """
    )

    rows = cursor.fetchall()
    connection.close()

    results = []

    for row in rows:
        (
            chunk_id,
            document_id,
            chunk_index,
            content,
            embedding_json,
            filename,
        ) = row

        try:
            chunk_embedding = np.array(
                json.loads(embedding_json),
                dtype=np.float32,
            )
        except (json.JSONDecodeError, TypeError):
            continue

        # Cosine similarity
        similarity = float(
            np.dot(
                query_embedding,
                chunk_embedding,
            )
        )

        # Çok düşük alakalı sonuçları alma
        if similarity < min_similarity:
            continue

        results.append(
            {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "chunk_index": chunk_index,
                "content": content,
                "filename": filename,
                "similarity": similarity,
            }
        )

    # En yüksek benzerlik önce
    results.sort(
        key=lambda item: item["similarity"],
        reverse=True,
    )

    return results[:top_k]


if __name__ == "__main__":

    print("=" * 70)
    print("ATLAS - RAG ARAMA TESTİ")
    print("=" * 70)

    query = input("\nSorunuzu yazın: ")

    results = search_documents(
        query,
        top_k=5,
        min_similarity=0.25,
    )

    print("\n" + "=" * 70)
    print("EN ALAKALI SONUÇLAR")
    print("=" * 70)

    if not results:
        print("\nBu soruyla ilgili yeterli sonuç bulunamadı.")
    else:

        for index, result in enumerate(
            results,
            start=1,
        ):

            print(f"\nSONUÇ {index}")

            print(
                f"Dosya: {result['filename']}"
            )

            print(
                f"Chunk: {result['chunk_index']}"
            )

            print(
                f"Benzerlik: "
                f"{result['similarity']:.4f}"
            )

            print("-" * 70)

            print(
                result["content"]
            )