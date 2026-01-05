"""
CV Upload API routes - Xử lý upload và phân tích CV
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from typing import Optional
from models import CVAnalysisResponse, JobRecommendationResponse, JobRecommendation
from services.cv_service import get_cv_service
from services.vector_service import search_jobs_vector, collection

router = APIRouter(prefix="/api/cv", tags=["CV"])


@router.post("/upload", response_model=CVAnalysisResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload và phân tích CV PDF
    
    Args:
        file: File PDF được upload
        
    Returns:
        CVAnalysisResponse: Thông tin đã phân tích từ CV
    """
    try:
        # Kiểm tra file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Chỉ chấp nhận file PDF"
            )
        
        # Đọc file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File rỗng"
            )
        
        # Phân tích CV
        cv_service = get_cv_service()
        analysis = cv_service.analyze_cv(content)
        
        if not analysis.get("success"):
            return CVAnalysisResponse(
                success=False,
                error=analysis.get("error", "Không thể phân tích CV")
            )
        
        return CVAnalysisResponse(
            success=True,
            email=analysis.get("email"),
            phone=analysis.get("phone"),
            skills=analysis.get("skills", []),
            experience_years=analysis.get("experience_years"),
            message="Phân tích CV thành công"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý CV: {str(e)}"
        )


@router.post("/recommend-jobs", response_model=JobRecommendationResponse)
async def recommend_jobs_from_cv(
    file: UploadFile = File(...),
    top_k: int = Query(default=10, ge=1, le=50, description="Số lượng công việc gợi ý")
):
    """
    Upload CV và nhận gợi ý công việc phù hợp
    
    Args:
        file: File PDF CV
        top_k: Số lượng công việc muốn gợi ý (1-50)
        
    Returns:
        JobRecommendationResponse: Danh sách công việc phù hợp
    """
    try:
        # Kiểm tra file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Chỉ chấp nhận file PDF"
            )
        
        # Đọc và phân tích CV
        content = await file.read()
        cv_service = get_cv_service()
        analysis = cv_service.analyze_cv(content)
        
        if not analysis.get("success"):
            raise HTTPException(
                status_code=400,
                detail=f"Không thể phân tích CV: {analysis.get('error')}"
            )
        
        # Tạo query tìm kiếm dựa trên CV
        search_query = cv_service.create_job_search_query(analysis)
        
        if not search_query:
            raise HTTPException(
                status_code=400,
                detail="Không thể tạo query tìm kiếm từ CV"
            )
        
        print(f"\n🔍 Search Query: {search_query}")
        
        # Tìm kiếm công việc phù hợp
        results = collection.query(
            query_texts=[search_query],
            n_results=top_k
        )
        
        # Xử lý kết quả
        jobs = []
        if results['documents'] and results['ids'] and results['distances']:
            documents = results['documents'][0]
            ids = results['ids'][0]
            distances = results['distances'][0]
            
            for i in range(len(ids)):
                # Convert distance thành relevance score (0-1)
                # Distance càng nhỏ = càng phù hợp
                relevance = max(0, 1 - (distances[i] / 2.0))
                
                jobs.append(JobRecommendation(
                    job_id=ids[i],
                    description=documents[i],
                    relevance_score=round(relevance, 3)
                ))
        
        # Tạo CV summary
        cv_summary = {
            "skills": analysis.get("skills", []),
            "experience_years": analysis.get("experience_years"),
            "email": analysis.get("email"),
            "phone": analysis.get("phone")
        }
        
        return JobRecommendationResponse(
            success=True,
            jobs=jobs,
            total=len(jobs),
            cv_summary=cv_summary,
            message=f"Tìm thấy {len(jobs)} công việc phù hợp với CV của bạn"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi tìm kiếm công việc: {str(e)}"
        )


@router.get("/test")
async def test_cv_endpoint():
    """Test endpoint để kiểm tra CV service hoạt động"""
    return {
        "status": "ok",
        "message": "CV service is ready",
        "endpoints": {
            "upload": "/api/cv/upload - Upload và phân tích CV",
            "recommend": "/api/cv/recommend-jobs - Upload CV và nhận gợi ý công việc"
        }
    }
