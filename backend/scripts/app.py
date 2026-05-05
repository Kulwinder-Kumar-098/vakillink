import streamlit as st
import os
import json
from semantic_search import LegalSearchEngine

# Set page config for a premium look
st.set_page_config(
    page_title="Nyaya-AI | Legal Semantic Search",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #94a3b8;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .search-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 1rem;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .result-card {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border-left: 5px solid #38bdf8;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #818cf8;
    }
    
    .score-badge {
        background: rgba(56, 189, 248, 0.1);
        color: #38bdf8;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    
    .metadata-label {
        color: #64748b;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .case-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 0.5rem;
    }
    
    .legal-issue {
        font-style: italic;
        color: #cbd5e1;
        margin-bottom: 1rem;
    }
    
    .snippet-box {
        background: rgba(0, 0, 0, 0.2);
        padding: 1rem;
        border-radius: 8px;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #e2e8f0;
    }
    
    .sidebar-content {
        padding: 1.5rem;
    }
    
    /* Center search input */
    div[data-testid="stTextInput"] > div > div > input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem 1rem !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# Load engine once
@st.cache_resource
def load_engine():
    return LegalSearchEngine()

engine = load_engine()

# Sidebar for Filters
with st.sidebar:
    st.markdown("<h2 style='color:#38bdf8;'>🔎 Filters</h2>", unsafe_allow_html=True)
    
    # Get unique domains from loaded metadata
    domains = sorted(list(set([m['domain'] for m in engine.all_metadata])))
    selected_domain = st.selectbox("Select Legal Domain", ["All"] + domains)
    
    top_k = st.slider("Results to show", 3, 20, 5)
    
    st.divider()
    st.markdown("""
        ### About Nyaya-AI
        This is a high-performance semantic search engine for Indian Case Law.
        - **Model:** all-MiniLM-L6-v2
        - **Total Chunks:** 17,000+
        - **Processing:** normalized cosine similarity
    """)

# Main UI
st.markdown("<h1 class='main-title'>Nyaya-AI Search</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Indian Legal Case Intelligence & Retrieval</p>", unsafe_allow_html=True)

# Search Bar Area
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    query = st.text_input("", placeholder="e.g., Rights of under-trial prisoners in India...", label_visibility="collapsed")
    search_clicked = st.button("Search Intelligence", use_container_width=True)

if query or search_clicked:
    with st.spinner("Analyzing legal corpus..."):
        results = engine.search(query, top_k=top_k * 2) # Get more to filter by domain if needed
        
        # Filter by domain if selected
        if selected_domain != "All":
            results = [r for r in results if r['domain'] == selected_domain]
        
        # Trim to top_k
        results = results[:top_k]

    if not results:
        st.warning("No matches found for your query. Try different keywords.")
    else:
        st.markdown(f"### Found {len(results)} relevant legal precedents")
        
        for res in results:
            with st.container():
                st.markdown(f"""
                <div class="result-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="metadata-label">{res['domain']} | {res['subdomain']}</span>
                        <span class="score-badge">Match: {res['score']:.1%}</span>
                    </div>
                    <div class="case-title">{res['case_name']}</div>
                    <div class="legal-issue">Issue: {res['legal_issue']}</div>
                    <div class="snippet-box">{res['text'][:800]}...</div>
                    <div style="margin-top: 1rem; font-size: 0.8rem; color: #64748b;">
                        Source: <a href="{res['source']}" style="color: #38bdf8;">{res['source']}</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Expandable full text
                with st.expander("View Full Context"):
                    st.write(res['text'])
else:
    # Landing Page Visuals
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[0]:
        st.info("**Constitutional Law**\n\nFundamental rights, writ petitions, and state powers.")
    with cols[1]:
        st.info("**Criminal Justice**\n\nIPC, CrPC, and landmark judgments on bail/trial.")
    with cols[2]:
        st.info("**Civil & Family**\n\nProperty rights, divorce laws, and succession.")
