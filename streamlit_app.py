import os
import streamlit as st
import requests
from requests.exceptions import RequestException

API_URL = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="Agentic RAG Knowledge Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for rich aesthetics
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

/* Main Layout Styles */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Glassmorphism Title Card */
.title-container {
    background: linear-gradient(135deg, rgba(31, 58, 86, 0.4) 0%, rgba(20, 32, 48, 0.6) 100%);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 2.5rem;
    margin-bottom: 2.5rem;
    text-align: center;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

.title-text {
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 3rem;
    background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 50%, #1D4ED8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}

.subtitle-text {
    color: #94A3B8;
    font-size: 1.1rem;
    margin-top: 0.5rem;
    font-weight: 300;
}

/* Card Styling */
.card-answer {
    background-color: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.8rem;
    margin-bottom: 1.5rem;
    font-size: 1.05rem;
    line-height: 1.6;
}

.card-sources {
    background-color: rgba(15, 23, 42, 0.4);
    border-left: 4px solid #3B82F6;
    border-radius: 4px 12px 12px 4px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
}

/* Badge styles */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-supported {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-unsupported {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-unknown {
    background-color: rgba(245, 158, 11, 0.15);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}
/* Upload section styling */

div[data-testid="stFileUploader"] {
    margin-bottom: 8px;
}

div[data-testid="stButton"] button {
    width: 100%;
    border-radius: 12px;
    padding: 12px;
    font-weight: 600;
}

   /* Hide password eye icon */
[data-testid="stTextInput"] button {
    display: none !important;
}
                     
</style>
""", unsafe_allow_html=True)

# App Title Header
st.markdown("""
<div class="title-container">
    <h1 class="title-text"> Agentic RAG Assistant</h1>
    <p class="subtitle-text">Multi-Agent Knowledge Assistant Powered by Google Gemini</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
#
# Input for custom Gemini API Key
api_key_input = st.sidebar.text_input(
    "Google Gemini API Key",
    type="password",
    placeholder="Enter your Gemini Studio API key",
    help="Your API key remains local and is only sent to the backend to authenticate requests."
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Document Ingestion")

uploaded_file = st.sidebar.file_uploader(
    "Choose documents to index",
    type=["pdf", "docx", "txt", "csv"],
    help="Supports PDF, DOCX, CSV, and plain TXT files."
)

if uploaded_file is not None:

    st.sidebar.caption(f"📄 Selected: {uploaded_file.name}")

    upload_clicked = st.sidebar.button(
        "📤 Upload Document",
        use_container_width=True
    )

    if upload_clicked:

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        with st.sidebar.spinner("⏳ Parsing & Indexing document..."):
            try:
                resp = requests.post(
                    f"{API_URL}/upload",
                    files=files,
                    timeout=60
                )

                resp.raise_for_status()
                result = resp.json()

                st.sidebar.success(
                    f"✅ Indexed {result.get('chunks_indexed', 0)} chunks from '{uploaded_file.name}'!"
                )

            except RequestException as exc:
                st.sidebar.error(
                    f"❌ Upload failed. Ensure backend is running.\n\nDetails: {exc}"
                )
# st.sidebar.markdown("---")
# st.sidebar.markdown("""
# ### ⚡ System Status
# - **Vector DB**: ChromaDB (Local Persistent)
# - **Embedding Model**: `sentence-transformers`
# - **Agent Framework**: Dual-Agent (Reasoning + Verification)
# """)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Quick Actions")

if st.sidebar.button("📄 Summarize Documents", use_container_width=True):
    st.session_state["quick_query"] = (
        "Provide a comprehensive summary of all uploaded documents."
    )

# if st.sidebar.button("📝 Generate MCQs", use_container_width=True):
#     st.session_state["quick_query"] = (
#         "Generate 20 important MCQs from the uploaded documents."
#     )

if st.sidebar.button("💡 Explain Key Concepts", use_container_width=True):
    st.session_state["quick_query"] = (
        "Explain the most important concepts from the uploaded documents."
    )

if st.sidebar.button("📚 Create Study Plan", use_container_width=True):
    st.session_state["quick_query"] = (
        "Create a study plan based on the uploaded documents."
    )

# Chat Main View
st.subheader("💡 Query Knowledge Base")

default_query = st.session_state.get("quick_query", "")

query = st.text_input(
    "Ask a question based on uploaded documents:",
    value=default_query,
    placeholder="What would you like to know from the knowledge base?"
)

submit_query = st.button(
    "🚀 Submit Query",
    use_container_width=False
)

if st.session_state.get("quick_query"):
    submit_query = True

if submit_query and query:
    # Prepare headers with Custom Gemini API Key if entered
    headers = {}
    if api_key_input:
        headers["X-Gemini-API-Key"] = api_key_input

    with st.spinner("🧠 Retrieval & Verification Agents working..."):
        try:
            resp = requests.post(f"{API_URL}/chat", data={"query": query}, headers=headers, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            st.session_state["quick_query"] = ""

            if result.get("error"):
                st.error(result.get("message"))
                st.stop()
            
            # Extract output parameters
            answer = result.get("answer", "No answer returned.")
            verification = result.get("verification", {})
            sources = result.get("sources", [])
            
            # Show Answer Card
            st.markdown("### 🤖 Assistant Response")
            st.markdown(f"""
            <div class="card-answer">
                {answer}
            </div>
            """, unsafe_allow_html=True)
            
            # Show Verification Card
            st.markdown("### 🛡️ Agent Verification")
            is_supported = verification.get("supported")
            notes = verification.get("notes", "No verification notes provided.")
            
            if is_supported is True:
                badge_html = '<span class="badge badge-supported">Verified Supported</span>'
            elif is_supported is False:
                badge_html = '<span class="badge badge-unsupported">Unverified / Hallucination Risk</span>'
            else:
                badge_html = '<span class="badge badge-unknown">Verification Inconclusive</span>'
                
            st.markdown(f"""
            <div style="background-color: rgba(30, 41, 59, 0.3); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 1.5rem;">
                <div style="margin-bottom: 10px;">{badge_html}</div>
                <div style="font-size: 0.95rem; color: #94A3B8;"><b>Verification Notes:</b> {notes}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show Sources Card
            st.markdown("### 📁 Referenced Sources")
            if sources:
                for src in sources:
                    st.markdown(f"""
                    <div class="card-sources">
                        📖 <b>Source:</b> {src}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No sources referenced. Answer might be generated from LLM internal knowledge.")
                
        except RequestException as exc:
            st.error(f"❌ Error communicating with backend at {API_URL}. Is the backend running?\n\nDetails: {exc}")
