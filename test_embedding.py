from embedding.model import create_embedding


text = """
Bu belge yerel RAG asistanının test edilmesi
amacıyla oluşturulmuştur.
"""


embedding = create_embedding(text)


print()
print("=" * 60)
print("EMBEDDING TEST")
print("=" * 60)

print(f"Vektör boyutu: {len(embedding)}")

print()
print("İlk 10 değer:")

for value in embedding[:10]:
    print(value)