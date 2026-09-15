import streamlit as st
from ui.components import render_sources
def render_quiz(questions,source_results):
    with st.form("prep_ai_quiz"):
        ans={}
        for i,q in enumerate(questions,1):
            st.markdown(f"### Q{i}. {q['question']}")
            ans[i]=st.radio("Choose one:",list("ABCD"),format_func=lambda x,q=q:f"{x}. {q['options'][x]}",index=None,key=f"answer_{i}")
        submitted=st.form_submit_button("Submit Quiz",type="primary",use_container_width=True)
    if submitted:
        score=sum(ans.get(i)==q["correct_answer"] for i,q in enumerate(questions,1)); st.success(f"Score: {score}/{len(questions)}")
        for i,q in enumerate(questions,1):
            if ans.get(i)==q["correct_answer"]: st.success(f"Q{i}: Correct")
            elif ans.get(i) is None: st.warning(f"Q{i}: Not answered. Correct: {q['correct_answer']}")
            else: st.error(f"Q{i}: Your answer: {ans[i]} | Correct: {q['correct_answer']}")
            st.write(f"**Explanation:** {q['explanation']}")
            ids=set(q.get("source_chunk_ids",[])); matches=[r for r in source_results if r.chunk.chunk_id in ids]
            if matches: st.markdown("**Retrieved source:**"); render_sources(matches)
