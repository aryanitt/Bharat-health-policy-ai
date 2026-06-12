from fastapi import APIRouter
import langchain
import os

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "langchain_version": langchain.__version__,
        "has_google_key": "GOOGLE_API_KEY" in os.environ,
        "has_groq_key": "GROQ_API_KEY" in os.environ,
        "deploy_time": "2026-06-13T01:50:00"
    }
