from dataclasses import dataclass
import os, streamlit as st
def value(name,default=""):
    try:
        x=st.secrets.get(name)
        if x is not None: return str(x).strip()
    except Exception: pass
    return os.getenv(name,default).strip()
@dataclass(frozen=True)
class Settings:
    embedding_model:str; groq_api_key:str; groq_model:str; chunk_size:int; chunk_overlap:int
    top_k:int; semantic_weight:float; max_questions:int; generation_batch_size:int
settings=Settings(value("EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2"),value("GROQ_API_KEY"),value("GROQ_MODEL","openai/gpt-oss-120b"),
 int(value("CHUNK_SIZE","700")),int(value("CHUNK_OVERLAP","100")),int(value("TOP_K","8")),float(value("SEMANTIC_WEIGHT","0.70")),int(value("MAX_QUESTIONS","100")),int(value("GENERATION_BATCH_SIZE","10")))
