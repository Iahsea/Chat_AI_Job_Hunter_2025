"""
Pydantic models cho request/response
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ChatMessage(BaseModel):
    """Một tin nhắn trong cuộc hội thoại"""
    role: str = Field(..., description="Role: 'user' hoặc 'assistant'")
    content: str = Field(..., description="Nội dung tin nhắn")


class ChatRequest(BaseModel):
    """Request body cho API chat"""
    message: str = Field(..., min_length=1, description="Tin nhắn từ user")
    conversation_history: List[Dict] = Field(
        default=[],
        description="Lịch sử hội thoại trước đó"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Tôi muốn đặt phòng khách sạn ở Đà Nẵng",
                "conversation_history": [
                    {"role": "user", "content": "Xin chào"},
                    {"role": "assistant", "content": "Chào bạn! Tôi là trợ lý đặt phòng khách sạn. Tôi có thể giúp gì cho bạn?"}
                ]
            }
        }
    }


class ChatResponse(BaseModel):
    """Response trả về từ API chat"""
    response: str = Field(..., description="Câu trả lời từ AI")
    success: bool = Field(default=True, description="Trạng thái thành công")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "response": "Tuyệt vời! Đà Nẵng có nhiều khách sạn đẹp. Bạn muốn đặt phòng cho bao nhiêu người và trong khoảng thời gian nào ạ?",
                "success": True
            }
        }
    }


class HealthResponse(BaseModel):
    """Response cho health check endpoint"""
    status: str
    gemini_configured: bool
