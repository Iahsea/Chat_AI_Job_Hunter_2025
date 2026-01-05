"""
Chat API routes
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from typing import Optional, List, Dict
from models import ChatRequest, ChatResponse, HealthResponse
from services.gemini_service import get_gemini_service
from services.openai_service import get_openai_service
from services.openrouter_service import get_openrouter_service
from services.cv_service import get_cv_service
from config import get_settings
import json

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


@router.post("/api/chat", tags=["Chat"])
async def chat(
    message: str = Form(...),
    conversation_history: str = Form(default="[]"),
    file: Optional[UploadFile] = File(None)
):
    """
    Main chatbot endpoint - Hỗ trợ upload CV PDF kèm message
    
    Nhận tin nhắn từ user, có thể kèm file CV PDF.
    - Nếu có file CV: trích xuất text và đưa vào context cho AI xử lý
    - Nếu không có file: chat bình thường
    
    Args:
        message: Tin nhắn từ user
        conversation_history: Lịch sử chat dạng JSON string (mặc định: [])
        file: File CV PDF (optional)
        
    Returns:
        ChatResponse với câu trả lời từ AI
    """
    try:
        # Log request
        print("\n🚀 New Chat Request Received")
        print(f"Message: {message}")
        print(f"Has file: {file is not None}")
        
        # Parse conversation history
        try:
            history = json.loads(conversation_history)
        except:
            history = []
        
        print(f"History length: {len(history)}")
        
        # XỬ LÝ FILE CV NẾU CÓ
        cv_text = ""
        if file and file.filename.lower().endswith('.pdf'):
            print("📄 Đang xử lý file CV...")
            try:
                content = await file.read()
                cv_service = get_cv_service()
                cv_text = cv_service.extract_text_from_pdf(content)
                
                if cv_text and len(cv_text) >= 50:
                    print(f"✅ Đã trích xuất {len(cv_text)} ký tự từ CV")
                    # Thêm context CV vào message
                    message = f"Dựa vào nội dung CV sau đây:\n\n{cv_text}\n\n---\n\nCâu hỏi/Yêu cầu của tôi: {message}"
                else:
                    print("⚠️ CV quá ngắn hoặc không đọc được")
            except Exception as e:
                print(f"❌ Lỗi khi xử lý CV: {e}")
                # Nếu lỗi khi đọc CV, vẫn tiếp tục chat bình thường
        
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
            message=message,
            conversation_history=history
        )
        
        return {
            "response": ai_response,
            "success": True,
            "has_cv": bool(cv_text)
        }
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )
