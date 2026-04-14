import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import chat, health
from api.config import BASE_DIR

app = FastAPI(title="Bharat Health Policy AI Backend")

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(health.router, prefix="/api", tags=["Health"])

# Static Files
# Mount the root directory to serve HTML/JS files (Compatibility with current structure)
try:
    # BASE_DIR is 'api/' folder, so project root is one level up
    root_dir = os.path.dirname(BASE_DIR)
    app.mount("/", StaticFiles(directory=root_dir, html=True), name="static")
except Exception as e:
    print(f"Static mount failed: {e}")
