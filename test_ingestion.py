from ingestion.pipeline import ingest_file
from database.repository import (
    get_document_count,
    get_chunk_count,
)


result = ingest_file("test_document.txt")


print("\n" + "=" * 60)
print("INGESTION TAMAMLANDI")
print("=" * 60)

print(f"Document ID: {result['document_id']}")
print(f"Dosya: {result['filename']}")
print(f"Tür: {result['file_type']}")
print(f"Metin uzunluğu: {result['text_length']}")
print(f"Chunk sayısı: {len(result['chunks'])}")

print("\n" + "=" * 60)
print("DATABASE DURUMU")
print("=" * 60)

print(f"Toplam belge: {get_document_count()}")
print(f"Toplam chunk: {get_chunk_count()}")