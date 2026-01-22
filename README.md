# 🩺 Bharat Health Policy Genius 2.0

A National-Scale AI Assistant & Learning Hub for Indian Health Schemes.

**Architecture:**
- **Frontend**: Multi-Page Application (HTML/CSS/JS)
- **CMS**: JSON-driven Video & Content Management
- **Backend**: FastAPI (Serverless on Vercel)
- **AI**: LangGraph Agent + RAG (Official Government PDFs)

## 🚀 Key Features
- **Smart AI Chatbot**: Context-aware answers from official documents.
- **Video Learning Hub**: Curated YouTube tutorials on PM-JAY & NHM.
- **Schemes Explorer**: Browse active government health policies.
- **Admin Dashboard**: Manage content without coding.
- **Government-Style UI**: Accessible, responsive, and professional.

## 📂 Project Structure
```
/
  index.html          # Landing Page
  chat.html           # AI Assistant Page
  videos.html         # Video Hub
  schemes.html        # Schemes List
  admin.html          # Admin CMS
  
  /data/content.json  # CMS Database
  /js/nav.js          # Shared Navigation
  /js/app.js          # Logic for Videos/Schemes
  /js/cms.js          # Admin Logic
  
  /api/index.py       # FastAPI Backend
  style.css           # Global Styles
```

## 🛠️ Deployment (Vercel)
1. **Push to GitHub**: `git push`
2. **Import to Vercel**: Select **Other** framework.
3. **Environment**: Set `GROQ_API_KEY`.
4. **Deploy**: Enjoy your Production-Grade App.

## ⚙️ Local Development
1. Install dependencies: `pip install -r requirements.txt`
2. Run server: `uvicorn api.index:app --reload`
3. Visit: `http://127.0.0.1:8000`
