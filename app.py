import streamlit as st
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_classic.tools.retriever import create_retriever_tool

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

st.set_page_config(
    page_title="Bharat Health Policy Genius – AI Assistant",
    page_icon="🩺",
    layout="wide"
)

st.markdown("""
<style>
body {background-color:#0A0F24;}
div.stApp {background: linear-gradient(135deg,#020617,#0b1220,#0f172a,#111827);}
.big-title {text-align:center;color:white;font-size:36px;font-weight:900;}
.subtext {text-align:center;color:#cbd5f5;font-size:18px;}
.chat-box {background:#0b1220;padding:20px;border-radius:12px;border:1px solid #293042;}
.user-bubble {background:#1d4ed8;padding:12px;border-radius:12px;color:white;width:fit-content;margin-bottom:10px;}
.bot-bubble {background:#111827;padding:12px;border-radius:12px;color:#e5e7eb;border:1px solid #384152;width:fit-content;}
.footer {text-align:center;color:#9ca3af;padding-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='big-title'>🩺 Bharat Health Policy Genius – AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtext'>Your smart assistant for Ayushman Bharat • PM-JAY • NHM • Government Health Schemes</p>", unsafe_allow_html=True)

embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

docs1 = PyPDFLoader("all_docs/AB-PMJAY.pdf").load()
docs2 = PyPDFLoader("all_docs/ayushman_bharat.pdf").load()
docs3 = PyPDFLoader("all_docs/NHM_more_information.pdf").load()
docs4 = PyPDFLoader("all_docs/PM-JAY.pdf").load()

all_docs = docs1 + docs2 + docs3 + docs4

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(all_docs)

vectordb = FAISS.from_documents(chunks, embedding)
retriever = vectordb.as_retriever()

api_wrapper = WikipediaAPIWrapper(top_k_result=1, doc_content_chars_max=400)
wiki = WikipediaQueryRun(api_wrapper=api_wrapper)

arxiv = ArxivQueryRun(
    api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=300)
)

retriever_tool = create_retriever_tool(
    retriever,
    "health_policy_scheme_search",
    "Search official PDF health policy documents of India like PM-JAY, NHM"
)

tools = [wiki, arxiv, retriever_tool]

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="openai/gpt-oss-20b",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an AI Health Policy Assistant for India. Use retriever tool to fetch answers from PDFs first. Explain clearly. If unsure, say you are unsure."
     ),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True
)



st.markdown("📤 <b>Upload Health PDFs</b>", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    key="pdf_upload"
)

if uploaded_files:
    for pdf in uploaded_files:
        loader = PyPDFLoader(pdf)
        all_docs += loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(all_docs)
    vectordb = FAISS.from_documents(chunks, embedding)
    retriever = vectordb.as_retriever()
    st.success("PDFs uploaded successfully! Knowledge updated.")

query = st.text_input(
    "",
    placeholder="Ask your question about health policies...",
    label_visibility="hidden",
    key="user_query"
)

if query:
    st.markdown(f"<p class='user-bubble'>👤 {query}</p>", unsafe_allow_html=True)

    with st.spinner("🔍 Searching health policy documents..."):
        result = agent_executor.invoke({"input": query})

    st.markdown(f"<p class='bot-bubble'>🤖 {result['output']}</p>", unsafe_allow_html=True)

    with st.expander("📄 Source Documents Used"):
        if "intermediate_steps" in result:
            for action, observation in result["intermediate_steps"]:
                if action.tool == "health_policy_scheme_search":
                    st.write("🔎 Retrieved from PDFs:")
                    st.write(observation)
                    st.write("---")
        else:
            st.write("No PDF context returned.")

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<p class='footer'>Made with ❤️ for NGOs & Healthcare Support</p>", unsafe_allow_html=True)
