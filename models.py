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
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Tôi muốn tìm việc lập trình Python",
                "conversation_history": [
                    {"role": "user", "content": "Xin chào"},
                    {"role": "assistant", "content": "Chào bạn! Tôi có thể giúp gì?"}
                ]
            }
        }


class ChatResponse(BaseModel):
    """Response trả về từ API chat"""
    response: str = Field(..., description="Câu trả lời từ AI")
    success: bool = Field(default=True, description="Trạng thái thành công")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Tôi có thể giúp bạn tìm việc lập trình Python...",
                "success": True
            }
        }


class HealthResponse(BaseModel):
    """Response cho health check endpoint"""
    status: str
    gemini_configured: bool


class CVAnalysisResponse(BaseModel):
    """Response từ phân tích CV"""
    success: bool = Field(..., description="Trạng thái phân tích")
    email: Optional[str] = Field(None, description="Email từ CV")
    phone: Optional[str] = Field(None, description="Số điện thoại")
    skills: List[str] = Field(default=[], description="Danh sách kỹ năng")
    experience_years: Optional[int] = Field(None, description="Số năm kinh nghiệm")
    message: Optional[str] = Field(None, description="Thông báo")
    error: Optional[str] = Field(None, description="Lỗi nếu có")


class JobRecommendation(BaseModel):
    """Một công việc được gợi ý"""
    job_id: str = Field(..., description="ID công việc")
    description: str = Field(..., description="Mô tả công việc")
    relevance_score: float = Field(..., description="Độ phù hợp (0-1)")


class JobRecommendationResponse(BaseModel):
    """Response chứa danh sách công việc gợi ý"""
    success: bool = Field(..., description="Trạng thái")
    jobs: List[JobRecommendation] = Field(default=[], description="Danh sách công việc")
    total: int = Field(..., description="Tổng số công việc tìm thấy")
    cv_summary: Dict = Field(default={}, description="Tóm tắt thông tin CV")
    message: Optional[str] = Field(None, description="Thông báo")

