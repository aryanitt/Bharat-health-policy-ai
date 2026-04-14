import os
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directory for PDFs
DOCS_PATH = os.path.join(BASE_DIR, "all_docs")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Model configurations
LLM_MODEL = "llama-3.1-8b-instant"
TEMPERATURE = 0
