from app.database.sqlite_db import initialize_database
from app.core.config import (
    BASE_DIR,
    DATA_DIR,
    UPLOADS_DIR,
    DATABASE_PATH,
    create_directories,
)


def main():
    print("Local RAG Assistant baslatiliyor...")

    create_directories()
    initialize_database()

    print(f"Proje klasoru: {BASE_DIR}")
    print(f"Veri klasoru: {DATA_DIR}")
    print(f"Dosya yukleme klasoru: {UPLOADS_DIR}")
    print(f"Veritabani: {DATABASE_PATH}")

    print("\nSistem basariyla hazirlandi!")


if __name__ == "__main__":
    main()