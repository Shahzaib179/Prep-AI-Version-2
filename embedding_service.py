import numpy as np,streamlit as st
from sentence_transformers import SentenceTransformer
@st.cache_resource(show_spinner=False)
def load_model(name): return SentenceTransformer(name)
class EmbeddingService:
    def __init__(self,name): self.model_name=name; self.model=load_model(name)
    def embed(self,texts): return np.asarray(self.model.encode(texts,batch_size=32,show_progress_bar=False,normalize_embeddings=True,convert_to_numpy=True),dtype="float32")
