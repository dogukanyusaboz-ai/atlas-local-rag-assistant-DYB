# ATLAS — Local RAG Assistant

ATLAS is a local AI assistant that allows users to ask questions about their own documents using Retrieval-Augmented Generation (RAG).

The system processes documents locally, creates multilingual embeddings, retrieves relevant document sections, and generates answers using a local Ollama language model.

## Features

- Local AI assistant
- Retrieval-Augmented Generation (RAG)
- PDF, DOCX and TXT document support
- Multilingual embeddings
- SQLite-based document storage
- Local Ollama LLM
- Streamlit web interface
- Document upload and deletion
- Source and similarity information
- Conversation history
- No cloud API required for inference

## Tech Stack

- Python
- Streamlit
- Ollama
- Qwen 2.5 3B
- Sentence Transformers
- paraphrase-multilingual-MiniLM-L12-v2
- SQLite
- NumPy

## Project Structure

```text
local_rag_project/
│
├── app/
│   ├── assistant/
│   ├── core/
│   ├── database/
│   ├── embedding/
│   ├── ingestion/
│   └── retrieval/
│
├── main.py
├── streamlit_app.py
├── generate_embeddings.py
├── ingest_folder.py
├── add_embedding_column.py
├── test_embedding.py
└── test_ingestion.py
