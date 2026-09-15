import streamlit as st
def load_css():
    st.markdown("""<style>
    .stApp{background:linear-gradient(135deg,#f7f9fc,#eef3f8)}
    .block-container{max-width:1180px;padding-top:2rem;padding-bottom:4rem}
    .prep-hero{padding:2rem 2.2rem;border-radius:22px;background:linear-gradient(135deg,#111827,#243b53);color:white;margin-bottom:1.5rem;box-shadow:0 12px 35px rgba(15,23,42,.12)}
    .prep-hero h1{font-size:2.5rem;margin-bottom:.35rem}.prep-hero p{color:#dbeafe;font-size:1.05rem;margin:0}
    .metric-card{padding:1rem;border:1px solid #dbe3ec;border-radius:16px;background:white;margin-bottom:.8rem}
    .source-card{padding:1rem;border:1px solid #dbe3ec;border-radius:14px;background:white}
    .source-meta{font-size:.82rem;color:#64748b;margin-bottom:.45rem}.source-text{color:#1e293b;line-height:1.6}
    div.stButton>button{border-radius:10px;font-weight:600}
    </style>""",unsafe_allow_html=True)
