import sqlite3

from app.core.config import DATABASE_PATH, create_directories


def get_connection():
    """SQLite veritabanı bağlantısı oluşturur."""

    create_directories()

    connection = sqlite3.connect(DATABASE_PATH)

    return connection


def initialize_database():
    """Veritabanı tablolarını oluşturur."""

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding TEXT,

            FOREIGN KEY (document_id)
                REFERENCES documents(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()

    print("Veritabani basariyla hazirlandi.")