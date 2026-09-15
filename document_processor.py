import io,re
from pathlib import Path
from dataclasses import dataclass
from pypdf import PdfReader
from docx import Document
@dataclass
class DocumentRecord: filename:str; file_type:str; page_count:int|None; character_count:int
@dataclass
class Chunk: chunk_id:str; text:str; filename:str; page_number:int|None; chunk_index:int; file_type:str
def clean(s): return re.sub(r"\n{3,}","\n\n",re.sub(r"[ \t]+"," ",s.replace("\x00"," "))).strip()
def extract_pdf(b,n): return [(i,clean(p.extract_text() or "")) for i,p in enumerate(PdfReader(io.BytesIO(b)).pages,1) if clean(p.extract_text() or "")]
def extract_docx(b,n):
    x=clean("\n".join(p.text for p in Document(io.BytesIO(b)).paragraphs)); return [(None,x)] if x else []
def extract_txt(b,n): x=clean(b.decode("utf-8-sig","replace")); return [(None,x)] if x else []
def extract_md(b,n):
    x=b.decode("utf-8-sig","replace"); x=re.sub(r"^#{1,6}\s*","",x,flags=re.M); x=re.sub(r"\[([^]]+)\]\([^)]+\)",r"\1",x); x=clean(x); return [(None,x)] if x else []
def extract_document(b,n):
    s=Path(n).suffix.lower()
    if s==".pdf": return extract_pdf(b,n),"PDF"
    if s==".docx": return extract_docx(b,n),"DOCX"
    if s==".txt": return extract_txt(b,n),"TXT"
    if s==".md": return extract_md(b,n),"MD"
    raise ValueError("Unsupported file type")
def chunk_text(pages,fn,ft,size,overlap):
    out=[]; num=0
    for page,text in pages:
        w=text.split(); start=0
        while start<len(w):
            end=min(start+size,len(w)); t=" ".join(w[start:end]).strip()
            if t: out.append(Chunk(f"{Path(fn).stem}_{num}",t,fn,page,num,ft)); num+=1
            if end>=len(w): break
            start=max(start+1,end-overlap)
    return out
def process_files(files,chunk_size=700,overlap=100):
    docs=[]; chunks=[]
    for f in files:
        b=f.content if hasattr(f,"content") else (f.seek(0) or f.read())
        pages,ft=extract_document(b,f.name); chars=sum(len(t) for _,t in pages)
        docs.append(DocumentRecord(f.name,ft,len(pages) if ft=="PDF" else None,chars))
        chunks += chunk_text(pages,f.name,ft,chunk_size,overlap)
    return docs,chunks
