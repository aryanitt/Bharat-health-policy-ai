import streamlit as st
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain.tools.retriever import create_retriever_tool

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor


# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Bharat Health Policy Genius – AI Assistant",
    page_icon="🩺",
    layout="wide"
)

load_dotenv()

# ---------------- CACHED RESOURCES ----------------

@st.cache_resource
def get_embeddings():
    """Load and cache the embedding model to avoid reloading on every run."""
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@st.cache_resource
def get_vector_store():
    """Load, split, and index the default PDF documents once."""
    embedding = get_embeddings()
    
    # List of default documents
    pdf_files = [
        "all_docs/AB-PMJAY.pdf",
        "all_docs/ayushman_bharat.pdf",
        "all_docs/NHM_more_information.pdf",
        "all_docs/PM-JAY.pdf"
    ]
    
    all_docs = []
    # Check if files exist to avoid errors
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            loader = PyPDFLoader(pdf_path)
            all_docs.extend(loader.load())
    
    if not all_docs:
        # Fallback if no docs found (prevents crash)
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(all_docs)
    
    vectordb = FAISS.from_documents(chunks, embedding)
    return vectordb

# Initialize Session State for VectorDB if not present
# We copy the cached DB to session state so we can mutate it (add user PDFs) without affecting the cache
if "vectordb" not in st.session_state:
    cached_db = get_vector_store()
    if cached_db:
        # Create a deep copy or just use the cached one if we don't plan to save back to cache
        # modifying cached objects is risky, but for FAISS in memory it's okay if we don't invalidate cache
        # A safer way is to just use the cached one as base. 
        # For simplicity in this app, we'll just use the cached one as the starter.
        st.session_state.vectordb = cached_db
    else:
        st.session_state.vectordb = None

# ---------------- SIDEBAR ----------------
st.sidebar.markdown("## 🧠 Quick Questions")
st.sidebar.markdown("Ask common questions about **Indian Health Policies** 👇")

example_questions = [
    "What is Ayushman Bharat PM-JAY and who is eligible?",
    "What benefits are covered under PM-JAY?",
    "Difference between NHM and Ayushman Bharat?",
    "How can a rural citizen apply for PM-JAY?",
    "What diseases are covered under Ayushman Bharat?",
    "Is PM-JAY applicable for private hospitals?",
    "How does NHM improve maternal health in India?",
    "What documents are required for Ayushman Bharat?"
]

if "user_query" not in st.session_state:
    st.session_state.user_query = ""

for q in example_questions:
    if st.sidebar.button(q):
        st.session_state.user_query = q

st.sidebar.markdown("---")
st.sidebar.markdown("📌 *Powered by Government PDFs + Wikipedia*")

# ---------------- STYLES ----------------
st.markdown("""
<style>
body {background-color:#0A0F24;}
div.stApp {background: linear-gradient(135deg,#020617,#0b1220,#0f172a,#111827);}
.big-title {text-align:center;color:white;font-size:36px;font-weight:900;}
.subtext {text-align:center;color:#cbd5f5;font-size:18px;}
.user-bubble {background:#1d4ed8;padding:12px;border-radius:12px;color:white;width:fit-content;margin-bottom:10px;}
.bot-bubble {background:#111827;padding:12px;border-radius:12px;color:#e5e7eb;border:1px solid #384152;width:fit-content;}
.footer {text-align:center;color:#9ca3af;padding-top:20px;}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<h1 class='big-title'>🩺 Bharat Health Policy Genius – AI Assistant</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='subtext'>Your smart assistant for Ayushman Bharat • PM-JAY • NHM • Government Health Schemes</p>",
    unsafe_allow_html=True
)

# ---------------- TOOLS ----------------
wiki = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=400)
)

arxiv = ArxivQueryRun(
    api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=300)
)

# Create retriever tool dynamically based on current vectordb state
if st.session_state.vectordb:
    retriever = st.session_state.vectordb.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "health_policy_scheme_search",
        "Search official Indian health policy PDFs like PM-JAY, NHM"
    )
    tools = [wiki, arxiv, retriever_tool]
else:
    tools = [wiki, arxiv]

# ---------------- LLM ----------------
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="openai/gpt-oss-20b", # Ensure this model name is correct for Groq
    temperature=0
)

# ---------------- PROMPT ----------------
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an AI Health Policy Assistant for India. "
        "Always use the PDF retriever first. "
        "Explain in simple language. "
        "If information is not found, say you are unsure."
    ),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# ---------------- AGENT ----------------
agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True
)

# ---------------- PDF UPLOAD ----------------
st.markdown("📤 <b>Upload Health PDFs</b>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed"
)

# Handle Uploads
if uploaded_files and st.session_state.vectordb:
    # Use a flag to avoid reprocessing the same files if possible, 
    # but Streamlit re-runs scripts, so we need to be careful.
    # For now, we'll assume the user uploads only when needed.
    
    new_docs = []
    for pdf in uploaded_files:
        # Note: PyPDFLoader typically needs a file path. 
        # Streamlit uploaded_files are file-like objects.
        # We need to save them temporarily or use a loader that supports streams.
        # PyPDFLoader in LangChain typically takes a path.
        
        # Workaround: Save to temp
        with open(f"temp_{pdf.name}", "wb") as f:
            f.write(pdf.getbuffer())
            
        loader = PyPDFLoader(f"temp_{pdf.name}")
        new_docs.extend(loader.load())
        
        # Cleanup
        os.remove(f"temp_{pdf.name}")

    if new_docs:
        embedding = get_embeddings()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(new_docs)
        # Add to existing session state DB
        st.session_state.vectordb.add_documents(chunks)
        st.success("✅ PDFs uploaded successfully! Knowledge updated.")


# ---------------- QUERY INPUT ----------------
query = st.text_input(
    "",
    value=st.session_state.user_query,
    placeholder="Ask your question about health policies...",
    label_visibility="hidden"
)

# ---------------- QUERY EXECUTION ----------------
if query:
    st.markdown(f"<p class='user-bubble'>👤 {query}</p>", unsafe_allow_html=True)

    with st.spinner("🔍 Searching health policy documents..."):
        try:
            result = agent_executor.invoke({"input": query})
            
            st.markdown(
                f"<p class='bot-bubble'>🤖 {result['output']}</p>",
                unsafe_allow_html=True
            )

            with st.expander("📄 Source Documents Used"):
                if result.get("intermediate_steps"):
                    for action, observation in result.get("intermediate_steps", []):
                        if hasattr(action, 'tool') and action.tool == "health_policy_scheme_search":
                            st.write("🔎 Retrieved from PDFs:")
                            st.write(observation)
                            st.write("---")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# ---------------- FOOTER ----------------
st.markdown(
    "<p class='footer'>Made with ❤️ for NGOs & Healthcare Support</p>",
    unsafe_allow_html=True
)
