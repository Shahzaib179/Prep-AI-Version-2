from dataclasses import dataclass
from retrieval.keyword_search import score
@dataclass
class RetrievalResult: chunk:object; semantic_score:float; keyword_score:float; hybrid_score:float
class HybridRetriever:
    def __init__(self,store,embedding_service,semantic_weight=.7): self.store=store; self.embedding_service=embedding_service; self.semantic_weight=semantic_weight
    def search(self,q,top_k=8):
        raw=self.store.search(self.embedding_service.embed([q]),min(max(top_k*3,top_k),len(self.store.chunks)))
        out=[RetrievalResult(c,s,score(q,c.text),self.semantic_weight*s+(1-self.semantic_weight)*score(q,c.text)) for c,s in raw]
        out.sort(key=lambda x:x.hybrid_score,reverse=True); return out[:top_k]
