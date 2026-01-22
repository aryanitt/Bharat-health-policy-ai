# 🩺 Bharat Health Policy Genius – AI Assistant

Bharat Health Policy Genius is an AI-powered assistant designed to help users understand India’s key health schemes.

**Architecture:**
- **Frontend**: HTML/CSS/JS (Static, Premium UI)
- **Backend**: FastAPI (Python Serverless Function)
- **Deployment**: Vercel Native

## 🚀 Features
- 🤖 Smart AI Chat Assistant  
- 📚 RAG with Official Government PDFs  
- ⚡ Serverless Architecture  

## 📂 Project Structure
```
/api          # Python Backend (FastAPI)
  /all_docs   # PDF Documents
  index.py    # Main API Logic
index.html    # Frontend Entry
style.css     # Premium Styles
script.js     # Frontend Logic
vercel.json   # Deployment Config
requirements.txt # Python Dependencies
```

## 🛠️ Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run Backend: `uvicorn api.index:app --reload`
3. Serve Frontend: Open `index.html` in browser (or use Live Server).
