import streamlit as st
import httpx
import os

# Adjust URL based on how you start the FastAPI server
API_URL = "http://localhost:8000/api/v1/ai"

def _call_api(endpoint: str, payload: dict) -> dict:
    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(f"{API_URL}{endpoint}", json=payload)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        st.error(f"Failed to contact backend: {e}")
        return {}

st.set_page_config(
    page_title="Vakilink - Legal RAG Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS (premium look) -------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    .stApp {background: linear-gradient(135deg,#0f172a,#1e1b4b);color:#f8fafc;}
    .main-title {font-size:3.5rem;font-weight:800;
        background:linear-gradient(90deg,#38bdf8,#818cf8);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .sub-title {font-size:1.2rem;color:#94a3b8;text-align:center;margin-bottom:2rem;}
    .search-card {background:rgba(255,255,255,0.05);backdrop-filter:blur(10px);
        border-radius:1rem;padding:2rem;border:1px solid rgba(255,255,255,0.1);}
    .result-card {background:rgba(30,41,59,0.7);border-left:5px solid #38bdf8;
        border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;transition:transform .2s;}
    .result-card:hover {transform:translateY(-5px);box-shadow:0 10px 25px -5px rgba(0,0,0,.3);}
    .score-badge {background:rgba(56,189,248,.1);color:#38bdf8;padding:.2rem .6rem;
        border-radius:20px;font-size:.8rem;font-weight:600;border:1px solid rgba(56,189,248,.3);}
    .metadata-label {color:#64748b;font-size:.85rem;text-transform:uppercase;}
    .case-title {font-size:1.25rem;font-weight:700;color:#f1f5f9;margin-bottom:.5rem;}
    .legal-issue {font-style:italic;color:#cbd5e1;margin-bottom:1rem;}
    .snippet-box {background:rgba(0,0,0,.2);padding:1rem;border-radius:8px;
        font-size:.95rem;line-height:1.6;color:#e2e8f0;}
    .sidebar-content {padding:1.5rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---- Sidebar filters -----------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#38bdf8;'>🔎 Filters</h2>", unsafe_allow_html=True)

    # Domain filter (populated from the backend)
    try:
        domain_resp = httpx.get(f"{API_URL}/domains", timeout=5)
        domains = ["All"] + domain_resp.json()
    except Exception:
        domains = ["All", "constitutional", "criminal", "consumer",
                  "family", "labour", "motor_accident", "general"]

    selected_domain = st.selectbox("Select Legal Domain", domains, index=0)
    top_k = st.slider("Results to show", 3, 20, 5)

st.markdown("<h1 class='main-title'>Vakilink</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='sub-title'>Legal AI assistant - ask any Indian law question</p>",
    unsafe_allow_html=True,
)

# ---- Search UI ---------------------------------------------------------------
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    query = st.text_input(
        "",
        placeholder="e.g., What are the rights of under-trial prisoners in India?",
        label_visibility="collapsed",
    )
    search_clicked = st.button("Search", use_container_width=True)

# ---- Main logic --------------------------------------------------------------
if query and (search_clicked or query.strip()):
    with st.spinner("🔎 Retrieving relevant cases…"):
        payload = {
            "query": query,
            "top_k": top_k,
            "domain": selected_domain if selected_domain != "All" else None,
            "use_hybrid": True,
            "use_reranker": False,
            "include_chunks": True,
        }
        resp = _call_api("/query", payload)

        if not resp:
            st.stop()

        answer = resp.get("answer", "No answer returned.")
        sources = resp.get("chunks", [])

    # ---- Display answer -------------------------------------------------------
    st.markdown(f"### Answer")
    st.success(answer)

    # ---- Show sources ---------------------------------------------------------
    if sources:
        st.markdown(f"#### Supporting Cases (showing {len(sources)})")
        for src in sources:
            with st.container():
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span class="metadata-label">{src.get('domain','')} | {src.get('subdomain','')}</span>
                            <span class="score-badge">Score {src.get('score',0):.2f}</span>
                        </div>
                        <div class="case-title">{src.get('case_name','')}</div>
                        <div class="legal-issue">Issue: {src.get('legal_issue','')}</div>
                        <div class="snippet-box">{src.get('text','')[:800]}...</div>
                        <div style="margin-top:1rem;font-size:0.8rem;color:#64748b;">
                            Source: <a href="{src.get('source','')}" style="color:#38bdf8;">{src.get('source','')}</a>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("Full text"):
                    st.write(src.get("text", ""))

else:
    # ---- Landing page ---------------------------------------------------------
    st.markdown(
        """
        <div style="height:40px;"></div>
        <div style="display:flex;justify-content:space-around;">
            <div style="background:rgba(255,255,255,0.05);padding:1rem;border-radius:8px;">
                <strong>Constitutional Law</strong><br/>Fundamental rights, writs, state powers.
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:1rem;border-radius:8px;">
                <strong>Criminal Justice</strong><br/>IPC, CrPC, bail & trial.
            </div>
            <div style="background:rgba(255,255,255,0.05);padding:1rem;border-radius:8px;">
                <strong>Civil & Family</strong><br/>Property, divorce, succession.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
