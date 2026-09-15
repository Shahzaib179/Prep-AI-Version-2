from __future__ import annotations
import streamlit as st
from config import settings

# Streamlit Cloud runs on Linux and is case-sensitive.  If the optional
# `ui` package is not included in the deployment, keep the app running with
# lightweight fallbacks instead of failing at startup.
try:
    from ui.styles import load_css
    from ui.components import render_header, render_document_info, render_sources
except ModuleNotFoundError as e:
    if not (str(e).startswith("No module named 'ui'") or
            str(e).startswith("No module named 'ui.styles'") or
            str(e).startswith("No module named 'ui.components'")):
        raise

    def load_css():
        return None

    def render_header():
        st.title("📚 Prep AI | MDCAT")

    def render_document_info(documents, chunks):
        st.info(f"{len(documents)} document(s) loaded • {len(chunks)} chunks")

    def render_sources(results):
        for i, result in enumerate(results, 1):
            chunk = getattr(result, "chunk", result)
            text = getattr(chunk, "text", str(chunk))
            st.markdown(f"**Source {i}**")
            st.write(text)

# Local-upload helper.  Streamlit Cloud can fail here when the optional
# `sources` package is missing from the deployed repository.  Keep the
# existing pipeline unchanged by converting Streamlit UploadedFile objects
# into the same simple name/content shape expected by the processor.
try:
    from sources.local_source import get_local_files
except ModuleNotFoundError as e:
    if not (str(e).startswith("No module named 'sources'") or
            str(e).startswith("No module named 'sources.local_source'")):
        raise

    class _UploadedDocument:
        def __init__(self, uploaded_file):
            self.name = uploaded_file.name
            self.content = uploaded_file.getvalue()
            self.size = len(self.content)

    def get_local_files(uploaded_files):
        return [_UploadedDocument(f) for f in uploaded_files]
from sources.google_drive import GoogleDriveSource
from ingestion.document_processor import process_files
from embeddings.embedding_service import EmbeddingService
from vectorstore.faiss_store import FAISSStore
from retrieval.hybrid_retriever import HybridRetriever
from generation.groq_generator import GroqGenerator
from validation.mcq_validator import validate_mcqs
from quiz.quiz_manager import render_quiz

st.set_page_config(page_title="Prep AI | MDCAT", page_icon="📚", layout="wide")
load_css()

def init_state():
    defaults = {"processed_signature": None, "documents": [], "chunks": [],
                "embedding_service": None, "vector_store": None, "retriever": None,
                "questions": [], "source_results": [], "drive_files": [], "generation_topic": ""}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v

def reset():
    for k in ["processed_signature","documents","chunks","embedding_service","vector_store","retriever","questions","source_results","drive_files","generation_topic"]:
        st.session_state[k] = None if k in ["processed_signature","embedding_service","vector_store","retriever"] else ([] if k in ["documents","chunks","questions","source_results","drive_files"] else "")

init_state()
render_header()

with st.sidebar:
    st.markdown("### ⚙️ RAG Settings")
    embedding_model=st.text_input("Embedding model", settings.embedding_model)
    top_k=st.slider("Hybrid results",3,15,settings.top_k)
    semantic_weight=st.slider("Semantic weight",0.0,1.0,settings.semantic_weight,0.05)
    chunk_size=st.slider("Chunk size (words)",300,1200,settings.chunk_size,50)
    overlap=st.slider("Chunk overlap (words)",30,250,settings.chunk_overlap,10)
    if st.button("Clear processed documents",use_container_width=True):
        reset(); st.rerun()

st.markdown("## 1. Add study material")
source=st.radio("Document source",["Local upload","Google Drive"],horizontal=True)
input_files=[]

if source=="Local upload":
    uploaded=st.file_uploader("Upload PDF, DOCX, TXT or Markdown files",type=["pdf","docx","txt","md"],accept_multiple_files=True)
    if uploaded: input_files=get_local_files(uploaded)
else:
    url=st.text_input("Google Drive file or folder link",placeholder="https://drive.google.com/...")
    st.caption("Drive access requires GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON in Streamlit Secrets and sharing the file/folder with that service account.")
    if url and st.button("Load from Google Drive",type="primary"):
        try:
            with st.spinner("Loading supported Drive files..."):
                st.session_state.drive_files=GoogleDriveSource().load(url)
            st.success(f"Loaded {len(st.session_state.drive_files)} supported file(s).")
        except Exception as e: st.error(str(e))
    input_files=st.session_state.drive_files

if input_files:
    signature=tuple((f.name,getattr(f,"size",len(getattr(f,"content",b"")))) for f in input_files)
    if signature != st.session_state.processed_signature:
        if st.button("Process documents",type="primary",use_container_width=True):
            with st.spinner("Extracting and chunking..."):
                docs,chunks=process_files(input_files,chunk_size,overlap)
            if not chunks: st.error("No usable text was extracted."); st.stop()
            with st.spinner("Creating embeddings once..."):
                service=EmbeddingService(embedding_model); vectors=service.embed([c.text for c in chunks])
            with st.spinner("Building FAISS index..."):
                store=FAISSStore(); store.build(vectors,chunks)
            st.session_state.update({"processed_signature":signature,"documents":docs,"chunks":chunks,
                "embedding_service":service,"vector_store":store,"retriever":HybridRetriever(store,service,semantic_weight),
                "questions":[],"source_results":[]})
            st.success(f"Processed {len(docs)} document(s) and created {len(chunks)} chunks.")

if st.session_state.chunks: render_document_info(st.session_state.documents,st.session_state.chunks)

st.markdown("## 2. Choose chapter or topic")
if not st.session_state.retriever:
    st.info("Process documents to unlock search and MCQ generation."); st.stop()

topic=st.text_input("Chapter, topic, subtopic or concept",placeholder="Example: Cell membrane and transport")
c1,c2=st.columns(2)
with c1: difficulty=st.selectbox("MCQ difficulty",["MDCAT Standard","Moderate","Challenging"])
with c2: count=st.number_input("Maximum MCQs",5,settings.max_questions,20,5)

if st.button("🔎 Find relevant content",use_container_width=True):
    if not topic.strip(): st.warning("Enter a topic first.")
    else:
        with st.spinner("Running hybrid search..."):
            r=HybridRetriever(st.session_state.vector_store,st.session_state.embedding_service,semantic_weight)
            st.session_state.retriever=r; st.session_state.source_results=r.search(topic.strip(),top_k)
if st.session_state.source_results:
    st.markdown("### Retrieved context"); render_sources(st.session_state.source_results)

st.markdown("## 3. Generate MDCAT MCQs")
if st.button("🧠 Generate maximum valid MCQs",type="primary",use_container_width=True):
    if not topic.strip(): st.warning("Enter a topic first."); st.stop()
    if not st.session_state.source_results:
        st.session_state.source_results=st.session_state.retriever.search(topic.strip(),top_k)
    if not st.session_state.source_results: st.error("No relevant content found."); st.stop()
    gen=GroqGenerator(settings.groq_api_key,settings.groq_model)
    all_q=[]; previous=[]; target=int(count); progress=st.progress(0)
    with st.spinner("Generating source-grounded MDCAT questions..."):
        for start in range(0,target,settings.generation_batch_size):
            n=min(settings.generation_batch_size,target-start)
            raw=gen.generate_mcqs(topic,st.session_state.source_results,n,difficulty,previous)
            valid=validate_mcqs(raw,{r.chunk.chunk_id for r in st.session_state.source_results})
            for q in valid:
                if len(all_q)>=target: break
                all_q.append(q); previous.append(q["question"])
            progress.progress(min(len(all_q)/target,1.0))
            if not valid: break
    progress.empty(); st.session_state.questions=all_q
    (st.success if all_q else st.error)(f"Generated {len(all_q)} valid MDCAT MCQs." if all_q else "No valid MCQs returned. Try a more specific topic.")

if st.session_state.questions:
    st.markdown("## 4. Take the quiz")
    render_quiz(st.session_state.questions,st.session_state.source_results)
