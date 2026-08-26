import ollama

from app.retrieval.search import search_documents


MODEL_NAME = "qwen2.5:3b"


def build_context(results):
    """
    RAG aramasından gelen chunk'ları
    LLM'in anlayabileceği kaynak metnine dönüştürür.
    """

    context_parts = []

    for index, result in enumerate(results, start=1):

        context_parts.append(
            f"""
[KAYNAK {index}]
Dosya: {result['filename']}
Chunk: {result['chunk_index']}
Benzerlik: {result['similarity']:.3f}

İçerik:
{result['content']}
"""
        )

    return "\n".join(context_parts)


def build_chat_history(messages, limit=6):
    """
    Son konuşmaları LLM'e gönderilecek
    metin haline getirir.
    """

    if not messages:
        return ""

    recent_messages = messages[-limit:]

    history_parts = []

    for message in recent_messages:

        role = message.get("role")
        content = message.get("content", "")

        if role == "user":

            history_parts.append(
                f"KULLANICI: {content}"
            )

        elif role == "assistant":

            history_parts.append(
                f"ATLAS: {content}"
            )

    return "\n".join(history_parts)


def get_previous_user_question(messages):
    """
    Sohbetteki son kullanıcı sorusunu bulur.
    """

    for message in reversed(messages):

        if message.get("role") == "user":

            return message.get(
                "content",
                "",
            )

    return ""


def is_continuation_question(question):
    """
    Sorunun önceki konuşmaya bağlı olup olmadığını
    anlamaya çalışır.
    """

    question_lower = question.lower().strip()

    continuation_phrases = [
        "peki",
        "bunun",
        "bunu",
        "bunlar",
        "bunların",
        "onun",
        "onu",
        "onlar",
        "projenin",
        "sistemin",
        "bununla",
        "bunun için",
        "neden gerekli",
        "neden gerekli?",
        "ne işe yarıyor",
        "ne işe yarıyor?",
        "daha detaylı",
        "daha fazla",
        "devam et",
        "devam",
    ]

    return any(
        phrase in question_lower
        for phrase in continuation_phrases
    )


def build_search_query(question, messages):
    """
    Devam sorularında önceki kullanıcı sorusunu da
    aramaya dahil ederek daha güçlü bir RAG sorgusu oluşturur.
    """

    if not messages:
        return question

    if not is_continuation_question(question):
        return question

    previous_question = get_previous_user_question(
        messages
    )

    if not previous_question:
        return question

    return f"""
Önceki kullanıcı sorusu:
{previous_question}

Yeni devam sorusu:
{question}

Bu iki sorunun birlikte ifade ettiği konuyu
belge içerisinde ara.
"""


def ask_assistant(
    question: str,
    messages=None,
):
    """
    Kullanıcı sorusunu alır.
    İlgili belgeleri bulur.
    Sohbet geçmişini dikkate alır.
    Yerel Ollama modelinden cevap üretir.
    """

    if messages is None:
        messages = []

    # --------------------------------------------------
    # 1. Sohbet geçmişini hazırla
    # --------------------------------------------------

    chat_history = build_chat_history(
        messages
    )

    # --------------------------------------------------
    # 2. RAG arama sorgusunu hazırla
    # --------------------------------------------------

    search_query = build_search_query(
        question,
        messages,
    )

    # --------------------------------------------------
    # 3. Belgelerde arama yap
    # --------------------------------------------------

    results = search_documents(
        search_query,
        top_k=5,
    )

    # Çok düşük benzerlikli sonuçları çıkar
    results = [
        result
        for result in results
        if result["similarity"] >= 0.15
    ]

    # --------------------------------------------------
    # 4. Sonuç yoksa LLM'e boş context gönderme
    # --------------------------------------------------

    if not results:

        return (
            "Belgelerde bu soruyla ilgili yeterli "
            "bilgi bulunamadı.",
            [],
        )

    # --------------------------------------------------
    # 5. Context oluştur
    # --------------------------------------------------

    context = build_context(
        results
    )

    # --------------------------------------------------
    # 6. LLM prompt'u
    # --------------------------------------------------

    prompt = f"""
Sen Atlas isimli yerel RAG belge asistanısın.

Görevin, kullanıcının sorularını verilen belge
kaynaklarına dayanarak cevaplamaktır.

ÇOK ÖNEMLİ KURALLAR:

1. Cevabın temel kaynağı BELGE KAYNAKLARIDIR.

2. Belgelerde bulunmayan bilgileri uydurma.

3. Belgelerde yeterli bilgi yoksa:
   "Belgelerde bu konuda yeterli bilgi bulunmuyor."
   şeklinde açıkça belirt.

4. Cevabı Türkçe ver.

5. Gereksiz uzun cevap verme.

6. Kullanıcının önceki konuşmasını anlamlandırmak için
   sohbet geçmişini kullanabilirsin.

7. Ancak önceki Atlas cevaplarını belge kaynağı gibi
   kabul etme.

8. "bu", "bunun", "bunlar", "onun", "projenin",
   "sistemin", "peki" gibi ifadeler önceki konuşmaya
   gönderme yapıyorsa neye gönderme yaptığını anlamaya
   çalış.

9. Kullanıcının sorusu bir önceki soruya bağlıysa,
   cevabı önceki konuşmanın bağlamını dikkate alarak ver.

10. Cevabı mümkün olduğunca doğrudan ver.

ÖNCEKİ SOHBET:

{chat_history}

BELGE KAYNAKLARI:

{context}

KULLANICININ YENİ SORUSU:

{question}

Şimdi yalnızca belge kaynaklarına dayanarak
kısa ve anlaşılır bir Türkçe cevap ver.

ATLAS:
"""

    # --------------------------------------------------
    # 7. Ollama üzerinden yerel LLM
    # --------------------------------------------------

    response = ollama.generate(
        model=MODEL_NAME,
        prompt=prompt,
    )

    answer = response.get(
        "response",
        "",
    ).strip()

    # --------------------------------------------------
    # 8. Cevabı döndür
    # --------------------------------------------------

    return answer, results


def main():

    print("=" * 60)
    print("ATLAS - YEREL RAG ASİSTANI")
    print("=" * 60)

    print(
        "\nÇıkmak için 'çıkış' yazabilirsiniz.\n"
    )

    messages = []

    while True:

        question = input("Sen: ").strip()

        # --------------------------------------------------
        # Çıkış
        # --------------------------------------------------

        if question.lower() in [
            "çıkış",
            "cikis",
            "exit",
            "quit",
        ]:

            print(
                "\nAtlas: Görüşmek üzere! 👋"
            )

            break

        # Boş soru
        if not question:
            continue

        print(
            "\nAtlas düşünüyor...\n"
        )

        try:

            answer, results = ask_assistant(
                question,
                messages,
            )

        except Exception as error:

            print(
                "\nAtlas hata verdi:"
            )

            print(error)

            print(
                "\n"
                + "-" * 60
            )

            continue

        # --------------------------------------------------
        # Cevap
        # --------------------------------------------------

        print("Atlas:")
        print(answer)

        # --------------------------------------------------
        # Sohbet geçmişine ekle
        # --------------------------------------------------

        messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        # --------------------------------------------------
        # Kaynaklar
        # --------------------------------------------------

        print(
            "\n" + "-" * 60
        )

        print(
            "KULLANILAN KAYNAKLAR"
        )

        print(
            "-" * 60
        )

        for result in results:

            print(
                f"- {result['filename']} "
                f"(chunk: {result['chunk_index']}, "
                f"benzerlik: "
                f"{result['similarity']:.3f})"
            )

        print()


if __name__ == "__main__":
    main()