from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Imports moved to functions for lazy loading
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import FAISS
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
# from langchain_groq import ChatGroq
# from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
# from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
# from langchain.agents import create_react_agent, AgentExecutor
# from langchain.tools.retriever import create_retriever_tool
# from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globals
EMBEDDINGS = None
VECTOR_DB = None

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []


def get_embeddings():
    from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
    global EMBEDDINGS
    if EMBEDDINGS is None:
        # Use API based embeddings (Lightweight)
        # Note: Requires HUGGINGFACEHUB_API_TOKEN env var
        api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        if not api_key:
            print("WARNING: HUGGINGFACEHUB_API_TOKEN missing. Embeddings will fail.")
            
        EMBEDDINGS = HuggingFaceInferenceAPIEmbeddings(
            api_key=api_key or "hf_dummy", # Prevent crash on startup, but will fail query if invalid
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    return EMBEDDINGS

def get_vector_store():
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    global VECTOR_DB
    if VECTOR_DB is None:
        embedding = get_embeddings()
        
        # Load default docs
        base_path = os.path.dirname(os.path.abspath(__file__))
        docs_path = os.path.join(base_path, "all_docs")
        
        # Ensure path exists
        if not os.path.exists(docs_path):
            os.makedirs(docs_path, exist_ok=True)
            
        pdf_files = [
            os.path.join(docs_path, "AB-PMJAY.pdf"),
            os.path.join(docs_path, "ayushman_bharat.pdf"),
            os.path.join(docs_path, "NHM_more_information.pdf")
        ]
        
        all_docs = []
        for pdf_path in pdf_files:
            if os.path.exists(pdf_path):
                loader = PyPDFLoader(pdf_path)
                all_docs.extend(loader.load())
        
        if all_docs:
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(all_docs)
            VECTOR_DB = FAISS.from_documents(chunks, embedding)
    
    return VECTOR_DB

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain.tools.retriever import create_retriever_tool
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    from langchain_groq import ChatGroq
    try:
        vectordb = get_vector_store()
        
        # Tools
        wiki = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=400)
        )
        arxiv = ArxivQueryRun(
            api_wrapper=ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=300)
        )
        
        tools = [wiki, arxiv]
        
        if vectordb:
            retriever = vectordb.as_retriever()
            retriever_tool = create_retriever_tool(
                retriever,
                "health_policy_scheme_search",
                "Search official Indian health policy PDFs like PM-JAY, NHM"
            )
            tools.append(retriever_tool)
        
        # LLM
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-8b-8192",
            temperature=0
        )
        
        system_msg = (
            "You are an AI Health Policy Assistant for India. "
            "Always use the PDF retriever first. "
            "Explain in simple language. "
            "If information is not found, say you are unsure."
        )
        
        # Create Agent (LangGraph) - using generic setup for compatibility
        agent_executor = create_react_agent(llm, tools)
        
        # Format History
        # Add System Message at the start
        messages = [SystemMessage(content=system_msg)]
        
        for msg in request.history:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))
        
        # Add current message
        messages.append(HumanMessage(content=request.message))
        
        # Run
        result = agent_executor.invoke({"messages": messages})
        
        # Extract last message content
        last_msg = result["messages"][-1]
        response_text = last_msg.content
        
        return {"response": response_text}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    try:
        global VECTOR_DB
        if VECTOR_DB is None:
            get_vector_store()
            
        new_docs = []
        for file in files:
            temp_path = f"/tmp/{file.filename}"
            # Ensure folder exists
            try:
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            except:
                # Fallback to local
                temp_path = file.filename
                
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            loader = PyPDFLoader(temp_path)
            new_docs.extend(loader.load())
            
        if new_docs:
            embedding = get_embeddings()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(new_docs)
            VECTOR_DB.add_documents(chunks)
            
        return {"status": "success", "message": "Files processed (Memory Only)"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- LOCAL DEV SERVER ----------------
from fastapi.staticfiles import StaticFiles

# Mount the root directory to serve index.html
try:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")
except Exception as e:
    print(f"Static mount failed: {e}")
