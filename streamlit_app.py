import streamlit as st
from pathlib import Path

from app.assistant.assistant import ask_assistant
from app.ingestion.pipeline import ingest_file
from app.database.repository import (
    get_documents,
    delete_document,
)
from app.core.config import UPLOADS_DIR


# =========================================================
# SAYFA AYARLARI
# =========================================================

st.set_page_config(
    page_title="ATLAS - Yerel AI Asistanı",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# TASARIM
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 16px;
        opacity: 0.7;
        margin-top: 0;
    }

    .document-card {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# BAŞLIK
# =========================================================

st.markdown(
    '<div class="main-title">🧠 ATLAS</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Yerel Yapay Zeka ve RAG Asistanı</div>',
    unsafe_allow_html=True,
)

st.divider()


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📚 Belgeler")

    documents = get_documents()

    if documents:

        st.caption(
            f"{len(documents)} belge sisteme kayıtlı"
        )

        st.divider()

        for document in documents:

            st.markdown(
                f"**📄 {document['filename']}**"
            )

            st.caption(
                f"{document['file_type']}  •  "
                f"{document['chunk_count']} chunk"
            )

            if st.button(
                "🗑️ Sil",
                key=f"delete_{document['id']}",
                use_container_width=True,
            ):

                delete_document(
                    document["id"]
                )

                file_path = (
                    UPLOADS_DIR
                    / document["filename"]
                )

                if file_path.exists():
                    file_path.unlink()

                st.success(
                    "Belge silindi."
                )

                st.rerun()

            st.divider()

    else:

        st.info(
            "Henüz sisteme belge eklenmedi."
        )

    st.subheader("📎 Yeni Belge")

    uploaded_file = st.file_uploader(
        "PDF, DOCX veya TXT",
        type=["pdf", "docx", "txt"],
    )

    if uploaded_file is not None:

        UPLOADS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            UPLOADS_DIR
            / uploaded_file.name
        )

        with open(
            file_path,
            "wb",
        ) as file:

            file.write(
                uploaded_file.getbuffer()
            )

        try:

            with st.spinner(
                "Belge işleniyor..."
            ):

                result = ingest_file(
                    str(file_path)
                )

            if result["already_exists"]:

                st.warning(
                    f"'{uploaded_file.name}' "
                    "zaten sisteme eklenmiş."
                )

            else:

                st.success(
                    f"'{uploaded_file.name}' "
                    f"eklendi. "
                    f"{len(result['chunks'])} chunk oluşturuldu."
                )

            st.rerun()

        except Exception as error:

            st.error(
                f"Belge işlenirken hata oluştu:\n\n{error}"
            )


# =========================================================
# SOHBET ALANI
# =========================================================

st.subheader("💬 Atlas ile Sohbet")

if not st.session_state.messages:

    st.info(
        "Merhaba! 👋\n\n"
        "Belgelerin hakkında bir soru sorabilirsin."
    )


for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and message.get("results")
        ):

            with st.expander(
                "📚 Kullanılan kaynaklar"
            ):

                for result in message["results"]:

                    st.markdown(
                        f"**📄 {result['filename']}**"
                    )

                    st.caption(
                        f"Chunk: {result['chunk_index']}  •  "
                        f"Benzerlik: "
                        f"{result['similarity']:.3f}"
                    )


# =========================================================
# CHAT INPUT
# =========================================================

question = st.chat_input(
    "Belgeleriniz hakkında bir soru sorun..."
)


if question:

    # Kullanıcı mesajını göster
    with st.chat_message("user"):

        st.markdown(question)

    # Backend'e mevcut geçmişi gönder
    with st.chat_message("assistant"):

        with st.spinner(
            "Atlas düşünüyor..."
        ):

            try:

                answer, results = ask_assistant(
                    question,
                    st.session_state.messages,
                )

            except Exception as error:

                answer = (
                    "Üzgünüm, cevap oluşturulurken "
                    "bir hata oluştu."
                )

                results = []

                st.error(
                    f"Hata: {error}"
                )

        st.markdown(answer)

        if results:

            with st.expander(
                "📚 Kullanılan kaynaklar"
            ):

                for result in results:

                    st.markdown(
                        f"**📄 {result['filename']}**"
                    )

                    st.caption(
                        f"Chunk: {result['chunk_index']}  •  "
                        f"Benzerlik: "
                        f"{result['similarity']:.3f}"
                    )

    # Geçmişe ekle
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "results": results,
        }
    )