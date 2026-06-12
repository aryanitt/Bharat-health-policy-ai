import os
from dotenv import load_dotenv

load_dotenv()

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directory for PDFs
DOCS_PATH = os.path.join(BASE_DIR, "all_docs")

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Model configurations
LLM_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0
