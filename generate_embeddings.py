import sqlite3
import json

from app.core.config import DATABASE_PATH
from app.embedding.model import create_embedding


def generate_missing_embeddings():

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, content
        FROM chunks
        WHERE embedding IS NULL
        """
    )

    chunks = cursor.fetchall()

    print(
        f"Embedding olusturulacak chunk sayisi: {len(chunks)}"
    )

    for chunk_id, content in chunks:

        print(
            f"Chunk isleniyor: {chunk_id}"
        )

        embedding = create_embedding(content)

        embedding_json = json.dumps(embedding)

        cursor.execute(
            """
            UPDATE chunks
            SET embedding = ?
            WHERE id = ?
            """,
            (
                embedding_json,
                chunk_id,
            ),
        )

        connection.commit()

    connection.close()

    print()
    print(
        "Tum embedding'ler basariyla olusturuldu."
    )


if __name__ == "__main__":
    generate_missing_embeddings()