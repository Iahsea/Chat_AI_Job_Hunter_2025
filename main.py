"""
AI JobHunter Chatbot - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config import get_settings
from routes.chat import router as chat_router
from routes.vector import router as vector_router
from routes.cv import router as cv_router

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="AI JobHunter Chatbot",
    version="1.0.0",
    description="AI Chatbot hỗ trợ tìm kiếm việc làm sử dụng Google Gemini"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(vector_router)
app.include_router(cv_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host,
        port=settings.port
    )
