import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from api.models.chat import ChatRequest, ChatResponse, UploadResponse
from api.services.agent_service import AgentService
from api.services.rag_service import RAGService
from api.config import DOCS_PATH

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response_text = await AgentService.chat(request.message, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=UploadResponse)
async def upload_file(files: List[UploadFile] = File(...)):
    from langchain_community.document_loaders import PyPDFLoader
    try:
        # Note: In the original logic, uploading didn't effectively live-update the BM25 retriever
        # without a restart or rebuild. For now, we maintain that logic but can improve it easily.
        
        for file in files:
            temp_path = os.path.join("/tmp", file.filename)
            try:
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            except:
                temp_path = file.filename
                
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Implementation for permanent storage if needed (logic from original was just to process and move on)
            # In a real app, we might move it to the DOCS_PATH
            # For now, keeping original logic's "process and acknowledge" style.
            
        # Reset retriever if we want to force re-indexing on next chat (optional improvement)
        # RAGService.reset_retriever()
            
        return UploadResponse(
            status="success", 
            message="Files uploaded successfully. (Note: Dynamic refresh might require session reset in this mode)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
