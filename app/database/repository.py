import sqlite3

from app.core.config import DATABASE_PATH, create_directories


def get_connection():
    """SQLite veritabanı bağlantısı oluşturur."""

    create_directories()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def save_document(
    filename: str,
    file_type: str,
    created_at: str,
    file_path: str = "",
) -> int:
    """Yeni belgeyi veritabanına kaydeder."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            filename,
            file_path,
            file_type,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            filename,
            file_path,
            file_type,
            created_at,
        ),
    )

    document_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return document_id


def save_chunk_with_embedding(
    document_id: int,
    chunk_index: int,
    content: str,
    embedding: str,
):
    """Chunk ve embedding bilgisini kaydeder."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO chunks (
            document_id,
            content,
            chunk_index,
            embedding
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            document_id,
            content,
            chunk_index,
            embedding,
        ),
    )

    connection.commit()
    connection.close()


def document_exists(filename: str) -> bool:
    """Belgenin daha önce eklenip eklenmediğini kontrol eder."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM documents
        WHERE filename = ?
        LIMIT 1
        """,
        (filename,),
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


def get_documents():
    """Tüm belgeleri ve chunk sayılarını getirir."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            documents.id,
            documents.filename,
            documents.file_path,
            documents.file_type,
            documents.created_at,
            COUNT(chunks.id) AS chunk_count
        FROM documents
        LEFT JOIN chunks
            ON chunks.document_id = documents.id
        GROUP BY documents.id
        ORDER BY documents.created_at DESC
        """
    )

    documents = cursor.fetchall()

    connection.close()

    return [dict(document) for document in documents]


def delete_document(document_id: int):
    """Belgeyi ve bağlı chunk'larını siler."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM chunks
        WHERE document_id = ?
        """,
        (document_id,),
    )

    cursor.execute(
        """
        DELETE FROM documents
        WHERE id = ?
        """,
        (document_id,),
    )

    connection.commit()
    connection.close()