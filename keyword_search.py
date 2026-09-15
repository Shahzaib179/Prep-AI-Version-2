import re
STOP={"the","a","an","and","or","of","to","in","on","for","with","from","by","is","are","was","were","what","which","how","why","about","chapter","topic"}
def words(q): return [w for w in re.findall(r"[A-Za-z0-9]+",q.lower()) if len(w)>2 and w not in STOP]
def score(q,text):
    ws=words(q); low=text.lower()
    return sum(bool(re.search(r"\b"+re.escape(w)+r"\b",low)) for w in ws)/len(set(ws)) if ws else 0.0
