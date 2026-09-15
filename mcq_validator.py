import re
def sim(a,b):
    x=set(re.findall(r"[a-z0-9]+",a.lower())); y=set(re.findall(r"[a-z0-9]+",b.lower()))
    return len(x&y)/len(x|y) if x and y else 0
def validate_mcqs(items,allowed_chunk_ids):
    out=[]; stems=[]
    for x in items:
        if not isinstance(x,dict): continue
        q=str(x.get("question","")).strip(); o=x.get("options",{}); a=str(x.get("correct_answer","")).upper().strip()
        ids=x.get("source_chunk_ids",[]); exp=str(x.get("explanation","")).strip()
        if not q or not isinstance(o,dict) or a not in "ABCD": continue
        o={k:str(o.get(k,"")).strip() for k in "ABCD"}
        if any(not v for v in o.values()) or len(set(v.lower() for v in o.values()))<4: continue
        if not isinstance(ids,list) or (ids and not set(map(str,ids)).issubset(allowed_chunk_ids)): continue
        if any(sim(q,s)>=.8 for s in stems): continue
        out.append({"question":q,"options":o,"correct_answer":a,"explanation":exp or "Supported by the retrieved context.","source_chunk_ids":[str(i) for i in ids]}); stems.append(q)
    return out
