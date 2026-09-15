import faiss,numpy as np
class FAISSStore:
    def __init__(self): self.index=None; self.chunks=[]
    def build(self,vectors,chunks):
        v=np.asarray(vectors,dtype="float32"); self.index=faiss.IndexFlatIP(v.shape[1]); self.index.add(v); self.chunks=list(chunks)
    def search(self,q,k=8):
        if self.index is None:return []
        scores,ids=self.index.search(np.asarray(q,dtype="float32"),min(k,len(self.chunks)))
        return [(self.chunks[int(i)],float(s)) for s,i in zip(scores[0],ids[0]) if i>=0]
