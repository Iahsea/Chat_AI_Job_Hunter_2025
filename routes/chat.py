"""
Chat API routes
"""
from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, HealthResponse
from services.gemini_service import get_gemini_service
from services.openai_service import get_openai_service
from services.openrouter_service import get_openrouter_service
from config import get_settings

router = APIRouter()


@router.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check đơn giản"""
    return {
        "status": "ok",
        "message": "AI JobHunter Chatbot is running!",
        "version": "1.0.0"
    }


@router.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Kiểm tra trạng thái service và cấu hình
    """
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        gemini_configured=bool(settings.GEMINI_API_KEY)
    )


@router.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Main chatbot endpoint
    
    Nhận tin nhắn từ user và trả về phản hồi từ AI (Google Gemini)
    
    Args:
        request: ChatRequest chứa message và conversation_history
        
    Returns:
        ChatResponse: Chứa response từ AI và success status
        
    Raises:
        HTTPException: Nếu có lỗi khi xử lý
    """
    try:
        # Log request
        print("\n🚀 New Chat Request Received")
        print(f"Message: {request.message}")
        print(f"History length: {len(request.conversation_history)}")
        
        # Lấy settings và chọn service phù hợp
        settings = get_settings()
        
        if settings.ai_service == "openai":
            print("Using OpenAI service")
            ai_service = get_openai_service()
        elif settings.ai_service == "openrouter":
            print("Using OpenRouter service (Free model)")
            ai_service = get_openrouter_service()
        else:
            print("Using Gemini service")
            ai_service = get_gemini_service()
        
        # Chat với AI
        ai_response = ai_service.chat(
            message=request.message,
            conversation_history=request.conversation_history
        )
        
        return ChatResponse(response=ai_response, success=True)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
