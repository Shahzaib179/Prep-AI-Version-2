# Prep AI Version 2
Modular RAG-based MDCAT preparation app.

Features: PDF/DOCX/TXT/MD extraction, metadata-aware chunking, Sentence Transformers embeddings, FAISS, keyword search, hybrid retrieval, Groq grounded MCQ generation, validation, quiz scoring, source display, Google Drive file/folder loading, Streamlit caching/session reuse.

## GitHub structure
Keep `app.py` at repository root:
```text
app.py
config.py
requirements.txt
runtime.txt
README.md
.env.example
.gitignore
.streamlit/config.toml
sources/
ingestion/
embeddings/
vectorstore/
retrieval/
generation/
validation/
quiz/
ui/
```
Do not commit `.env` or `.streamlit/secrets.toml`.

## Local
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Set `GROQ_API_KEY` in the environment or Streamlit Secrets.

## Streamlit Cloud
Main file: `app.py`
Secrets:
```toml
GROQ_API_KEY="your_key"
GROQ_MODEL="openai/gpt-oss-120b"
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
```

## Google Drive
Enable Drive API in Google Cloud, create a service account, share the Drive file/folder with its email, then add the complete JSON credentials as:
```toml
GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'
```
