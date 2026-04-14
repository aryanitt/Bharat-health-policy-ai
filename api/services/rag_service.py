import os
from typing import Optional
from api.config import DOCS_PATH

class RAGService:
    _retriever: Optional["BM25Retriever"] = None

    @classmethod
    def get_retriever(cls) -> Optional["BM25Retriever"]:
        """
        Singleton retriever instance. Loads and indexes PDFs if not already done.
        """
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_community.retrievers import BM25Retriever
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        if cls._retriever is None:
            # Ensure directory exists
            if not os.path.exists(DOCS_PATH):
                try:
                    os.makedirs(DOCS_PATH, exist_ok=True)
                except OSError:
                    pass # Resilience for read-only systems

            # Hardcoded list from original logic
            pdf_files = [
                os.path.join(DOCS_PATH, "AB-PMJAY.pdf"),
                os.path.join(DOCS_PATH, "ayushman_bharat.pdf"),
                os.path.join(DOCS_PATH, "NHM_more_information.pdf")
            ]
            
            all_docs = []
            for pdf_path in pdf_files:
                if os.path.exists(pdf_path):
                    try:
                        loader = PyPDFLoader(pdf_path)
                        all_docs.extend(loader.load())
                    except Exception as e:
                        print(f"Error loading {pdf_path}: {e}")
            
            if all_docs:
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = splitter.split_documents(all_docs)
                # Use BM25 for keyword-based retrieval
                cls._retriever = BM25Retriever.from_documents(chunks)
                cls._retriever.k = 4
                
        return cls._retriever

    @classmethod
    def reset_retriever(cls):
        """Reset the singleton instance (e.g., after new uploads)."""
        cls._retriever = None
