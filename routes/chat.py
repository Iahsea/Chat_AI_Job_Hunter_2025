"""
Chat API routes
"""
from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, HealthResponse
from services.gemini_service import get_gemini_service
from services.openrouter_service import get_openrouter_service
from database import db_manager, get_database_context, get_invoice_details_for_ai
from config import get_settings
import re

router = APIRouter()


@router.get("/", tags=["Health"])
async def root():
    """Root endpoint - Health check đơn giản"""
    return {
        "status": "ok",
        "message": "AI Hotel Management Chatbot is running! 🏨",
        "version": "1.0.0",
        "description": "Hệ thống chatbot AI hỗ trợ quản lý khách sạn"
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
    
    Nhận tin nhắn từ user và trả về phản hồi từ AI
    
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

        # Lấy toàn bộ context từ database để đưa vào AI
        db_context = get_database_context()
        print(f"📊 Database context loaded: {len(db_context)} characters")
        
        # Thêm database context vào tin nhắn để AI có đầy đủ thông tin
        enhanced_message = f"{request.message}\n\n--- DỮ LIỆU KHÁCH SẠN ---\n{db_context}"
        
        settings = get_settings()
        import os
        ai_service = os.getenv('AI_SERVICE', getattr(settings, 'AI_SERVICE', 'gemini')).lower()
        model = settings.ai_model
        gemini_models = ["gemini-1.0-pro", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro-vision", "gemini-1.5-pro-vision", "gemini-3-flash-preview"]
        openrouter_prefixes = ["mistralai/", "openrouter/", "meta-llama/", "google/", "anthropic/", "xiaomi/"]
        
        if ai_service == 'openrouter':
            if not any(model.startswith(prefix) for prefix in openrouter_prefixes):
                raise HTTPException(
                    status_code=400,
                    detail=f"Model '{model}' không hợp lệ cho OpenRouter. Vui lòng chọn model đúng chuẩn OpenRouter."
                )
            service = get_openrouter_service()
        elif ai_service == 'gemini':
            if model not in gemini_models:
                raise HTTPException(
                    status_code=400,
                    detail=f"Model '{model}' không hợp lệ cho Gemini. Vui lòng chọn model đúng chuẩn Gemini."
                )
            service = get_gemini_service()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"AI_SERVICE '{ai_service}' không được hỗ trợ."
            )
        
        # Gọi AI với message đã có database context
        ai_response = service.chat(
            message=enhanced_message,
            conversation_history=request.conversation_history
        )
        return ChatResponse(response=ai_response, success=True)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error: {str(e)}"
        )


# ============ DATABASE API ENDPOINTS ============

@router.get("/api/services", tags=["Database"])
async def get_services():
    """Lấy danh sách tất cả dịch vụ"""
    try:
        services = db_manager.get_all_services()
        return {"status": "success", "data": services}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/services/{service_id}", tags=["Database"])
async def get_service(service_id: int):
    """Lấy thông tin một dịch vụ theo ID"""
    try:
        service = db_manager.get_service_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Không tìm thấy dịch vụ")
        return {"status": "success", "data": service}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/rooms", tags=["Database"])
async def get_rooms(available_only: bool = False):
    """Lấy danh sách phòng"""
    try:
        if available_only:
            rooms = db_manager.get_available_rooms()
        else:
            rooms = db_manager.get_all_rooms()
        return {"status": "success", "data": rooms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/rooms/{room_id}", tags=["Database"])
async def get_room(room_id: int):
    """Lấy thông tin một phòng theo ID"""
    try:
        room = db_manager.get_room_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Không tìm thấy phòng")
        return {"status": "success", "data": room}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/customers", tags=["Database"])
async def get_customers():
    """Lấy danh sách khách hàng"""
    try:
        customers = db_manager.get_all_customers()
        return {"status": "success", "data": customers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/invoices", tags=["Database"])
async def get_invoices():
    """Lấy danh sách tất cả hóa đơn"""
    try:
        invoices = db_manager.get_all_invoices()
        return {"status": "success", "data": invoices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/invoices/{invoice_id}", tags=["Database"])
async def get_invoice(invoice_id: int):
    """Lấy chi tiết một hóa đơn"""
    try:
        invoice = db_manager.get_invoice_by_id(invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")
        services = db_manager.get_invoice_service_details(invoice_id)
        total = db_manager.get_invoice_total(invoice_id)
        return {
            "status": "success",
            "data": {
                "invoice": invoice,
                "services": services,
                "total": total
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stats/services", tags=["Database"])
async def get_service_stats():
    """Thống kê sử dụng dịch vụ"""
    try:
        stats = db_manager.get_service_revenue_stats()
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stats/revenue", tags=["Database"])
async def get_revenue_stats():
    """Thống kê doanh thu"""
    try:
        summary = db_manager.get_total_revenue_summary()
        monthly = db_manager.get_monthly_revenue()
        room_stats = db_manager.get_room_stats()
        return {
            "status": "success",
            "data": {
                "summary": summary,
                "monthly": monthly,
                "rooms": room_stats
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/db-status", tags=["Database"])
async def check_database_status():
    """Kiểm tra trạng thái kết nối database"""
    try:
        connection = db_manager.get_connection()
        if connection and connection.is_connected():
            connection.close()
            return {"status": "connected", "message": "Kết nối database thành công"}
        return {"status": "disconnected", "message": "Không thể kết nối database"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
