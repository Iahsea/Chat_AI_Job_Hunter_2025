"""
Vector API routes - Quản lý vector database
"""
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.vector_service import add_job_to_vector

router = APIRouter()


def clean_html(html_text):
    """Loại bỏ HTML tags và giữ lại text thuần"""
    if not html_text:
        return ""
    clean = re.sub(r'<[^>]+>', '', html_text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


class JobVectorRequest(BaseModel):
    """Request body để thêm công việc vào vector DB"""
    job_id: str
    name: str
    description: str
    location: str = ""
    salary: str = ""
    level: str = ""
    job_type: str = ""
    years_of_experience: str = ""
    end_date: str = ""
    start_date: str = ""
    work_mode: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123",
                "name": "Lập trình viên Python",
                "description": "Phát triển ứng dụng web bằng Python tại Hà Nội, lương 15-20 triệu.",
                "location": "Hà Nội",
                "salary": "15,000,000đ",
                "level": "Junior",
                "job_type": "Full-time",
                "years_of_experience": "1-2 năm",
                "end_date": "2026-12-31",
                "start_date": "2026-01-01",
                "work_mode": "Hybrid"
            }
        }


@router.post("/api/vector/add-job", tags=["Vector"])
async def add_job_vector(request: JobVectorRequest):
    """
    API để thêm công việc mới vào vector DB.
    Backend Spring Boot sẽ gọi endpoint này khi tạo công việc mới.
    """
    try:
        # Clean HTML từ description
        clean_description = clean_html(request.description)
        
        # Ghép thông tin job thành 1 đoạn text để vector hóa
        text = (
            f"{request.name}: {clean_description}\n"
            f"Địa điểm: {request.location}\n"
            f"Lương: {request.salary}\n"
            f"Cấp bậc: {request.level}\n"
            f"Loại hình: {request.job_type}\n"
            f"Kinh nghiệm: {request.years_of_experience}\n"
            f"Ngày bắt đầu: {request.start_date}\n"
            f"Ngày kết thúc: {request.end_date}\n"
            f"Hình thức làm việc: {request.work_mode}"
        )
        print(f"\n🆕 Thêm công việc vào vector DB: {request.job_id} - {text}")
        add_job_to_vector(request.job_id, text)
        return {
            "success": True, 
            "message": f"Đã thêm công việc {request.job_id} vào vector DB",
            "job_id": request.job_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi thêm vào vector DB: {str(e)}")
