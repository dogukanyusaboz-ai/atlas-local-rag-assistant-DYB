from pathlib import Path


# Projenin ana klasörü
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Veri klasörleri
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DATABASE_DIR = DATA_DIR / "database"

# Veritabanı dosyası
DATABASE_PATH = DATABASE_DIR / "local_rag.db"


def create_directories():
    """Gerekli proje klasörlerini oluşturur."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)