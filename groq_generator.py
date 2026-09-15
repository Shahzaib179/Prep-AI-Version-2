import json,re
from groq import Groq
from generation.prompts import build_mcq_prompt
def parse_json(s):
    s=s.strip(); s=re.sub(r"^```(?:json)?\s*|\s*```$","",s,flags=re.I)
    try:return json.loads(s)
    except: pass
    a=s.find("{"); b=s.rfind("}")
    if a>=0 and b>a:return json.loads(s[a:b+1])
    raise ValueError("Groq returned invalid JSON.")
class GroqGenerator:
    def __init__(self,key,model):
        if not key: raise RuntimeError("GROQ_API_KEY is missing. Add it to Streamlit Secrets.")
        self.client=Groq(api_key=key); self.model=model
    def generate_mcqs(self,topic,results,count,difficulty,previous_questions=None):
        r=self.client.chat.completions.create(model=self.model,temperature=.35,max_tokens=8192,messages=[{"role":"system","content":"Return only valid JSON source-grounded MDCAT MCQs."},{"role":"user","content":build_mcq_prompt(topic,results,count,difficulty,previous_questions or [])}])
        data=parse_json(r.choices[0].message.content or "")
        return data.get("questions",[]) if isinstance(data,dict) else (data if isinstance(data,list) else [])
