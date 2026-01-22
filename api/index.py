from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
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
from langchain_core.messages import HumanMessage, AIMessage

# Initialize App
app = FastAPI()
load_dotenv()

# Global State (Note: In serverless, this persists only for warm containers)
VECTOR_DB = None
EMBEDDINGS = None

class ChatRequest(BaseModel):
    message: str
    history: List[dict] # [{"role": "user", "content": "hi"}, ...]

def get_embeddings():
    global EMBEDDINGS
    if EMBEDDINGS is None:
        EMBEDDINGS = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return EMBEDDINGS

def get_vector_store():
    global VECTOR_DB
    if VECTOR_DB is None:
        embedding = get_embeddings()
        
        # Load default docs
        # Note: Paths are relative to the runtime root. In Vercel, it might vary.
        # We try safe paths.
        base_path = os.path.dirname(os.path.abspath(__file__))
        docs_path = os.path.join(base_path, "all_docs")
        
        pdf_files = [
            os.path.join(docs_path, "AB-PMJAY.pdf"),
            os.path.join(docs_path, "ayushman_bharat.pdf"),
            os.path.join(docs_path, "NHM_more_information.pdf"),
            os.path.join(docs_path, "PM-JAY.pdf")
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
            model_name="openai/gpt-oss-20b", # Keeping user's model name
            temperature=0
        )
        
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are an AI Health Policy Assistant for India. "
                "Always use the PDF retriever first. "
                "Explain in simple language. "
                "If information is not found, say you are unsure."
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # Format History
        chat_history = []
        for msg in request.history:
            if msg['role'] == 'user':
                chat_history.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                chat_history.append(AIMessage(content=msg['content']))
        
        # Run
        result = agent_executor.invoke({
            "input": request.message,
            "chat_history": chat_history
        })
        
        return {"response": result['output']}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(files: List[UploadFile] = File(...)):
    try:
        # Note: This updates the in-memory DB only for this container instance.
        # It won't persist across fresh cold starts or other containers.
        global VECTOR_DB
        if VECTOR_DB is None:
            get_vector_store()
            
        new_docs = []
        for file in files:
            # Save to temp
            temp_path = f"/tmp/{file.filename}"
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            loader = PyPDFLoader(temp_path)
            new_docs.extend(loader.load())
            
            # Cleanup? Maybe keep for a bit.
            # os.remove(temp_path) 
            
        if new_docs:
            embedding = get_embeddings()
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(new_docs)
            VECTOR_DB.add_documents(chunks)
            
        return {"status": "success", "message": "Files processed (Memory Only)"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
