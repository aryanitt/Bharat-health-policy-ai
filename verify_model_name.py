import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import time

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

candidates = [
    "models/gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash", 
    "gemini-pro"
]

for model in candidates:
    print(f"Testing model: {model}")
    try:
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key
        )
        response = llm.invoke("Hi")
        print(f"SUCCESS with {model}: {response.content}")
        break
    except Exception as e:
        print(f"FAILED {model}: {e}")
        time.sleep(1)
