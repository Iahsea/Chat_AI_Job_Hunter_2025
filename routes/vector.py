"""
Vector API routes - Quản lý vector database
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vector_service import add_job_to_vector

router = APIRouter()


class JobVectorRequest(BaseModel):
    """Request body để thêm công việc vào vector DB"""
    job_id: str
    title: str
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123",
                "title": "Lập trình viên Python",
                "description": "Phát triển ứng dụng web bằng Python tại Hà Nội, lương 15-20 triệu."
            }
        }


@router.post("/api/vector/add-job", tags=["Vector"])
async def add_job_vector(request: JobVectorRequest):
    """
    API để thêm công việc mới vào vector DB.
    Backend Spring Boot sẽ gọi endpoint này khi tạo công việc mới.
    """
    try:
        text = f"{request.title}: {request.description}"
        add_job_to_vector(request.job_id, text)
        return {
            "success": True, 
            "message": f"Đã thêm công việc {request.job_id} vào vector DB",
            "job_id": request.job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm vào vector DB: {str(e)}")
