import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(f"API Key present: {bool(api_key)}")

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0
    )
    print("Model initialized. Invoking...")
    response = llm.invoke("Hello, are you working?")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
