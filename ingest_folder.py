from pathlib import Path

from app.core.config import UPLOADS_DIR
from app.ingestion.pipeline import ingest_file


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
}


def ingest_uploads():
    """
    data/uploads klasöründeki desteklenen belgeleri
    veritabanına ekler.
    """

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    files = [
        file
        for file in UPLOADS_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        print("data/uploads klasöründe belge bulunamadı.")
        return

    print(f"{len(files)} belge bulundu.\n")

    for file in files:
        print("=" * 60)
        print(f"İşleniyor: {file.name}")
        print("=" * 60)

        try:
            result = ingest_file(str(file))

            if result.get("already_exists"):
                print("→ Daha önce eklenmiş, atlandı.")

            else:
                print(
                    f"→ Başarıyla database'e eklendi."
                    f" {len(result['chunks'])} chunk oluşturuldu."
                )

        except Exception as error:
            print(f"→ HATA: {error}")

        print()


if __name__ == "__main__":
    ingest_uploads()