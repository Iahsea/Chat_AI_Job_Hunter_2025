"""
AI Hotel Booking Chatbot - Main Application
Hệ thống chatbot AI hỗ trợ đặt phòng khách sạn
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from config import get_settings
from routes.chat import router as chat_router

# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="AI Hotel Booking Chatbot",
    version="1.0.0",
    description="AI Chatbot hỗ trợ tư vấn và đặt phòng khách sạn sử dụng Google Gemini"
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.host,
        port=settings.port
    )
