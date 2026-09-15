import streamlit as st
def render_header():
    st.markdown("""<div class="prep-hero"><h1>📚 Prep AI</h1><p>Advanced RAG-powered MDCAT preparation from your own study material.</p></div>""",unsafe_allow_html=True)
def render_document_info(docs,chunks):
    st.markdown("## Document information"); cols=st.columns(4)
    vals=[("Documents",len(docs)),("PDF pages",sum(d.page_count or 0 for d in docs) or "—"),("Characters",f"{sum(d.character_count for d in docs):,}"),("Chunks",f"{len(chunks):,}")]
    for c,(k,v) in zip(cols,vals):
        with c: st.markdown(f'<div class="metric-card"><div style="color:#64748b">{k}</div><div style="font-size:1.5rem;font-weight:700">{v}</div></div>',unsafe_allow_html=True)
    with st.expander("View loaded documents"):
        for d in docs: st.write(f"**{d.filename}** · {d.file_type} · Pages: {d.page_count if d.page_count else 'Not available'} · Characters: {d.character_count:,}")
def render_sources(results,expanded=False):
    for r in results:
        c=r.chunk; p=c.page_number if c.page_number is not None else "Not available"
        with st.expander(f"{c.filename} · Page {p} · Hybrid {r.hybrid_score:.3f}",expanded=expanded):
            st.markdown(f'<div class="source-card"><div class="source-meta">File: <b>{c.filename}</b> | Page: <b>{p}</b> | Semantic: <b>{r.semantic_score:.3f}</b> | Keyword: <b>{r.keyword_score:.3f}</b></div><div class="source-text">{c.text}</div></div>',unsafe_allow_html=True)
