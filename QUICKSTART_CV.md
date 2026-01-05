# 🎯 Quick Start - Upload CV & Tìm Việc

## Bước 1: Khởi động server

```bash
cd D:/D_CNTT/TTCS/AIJobHunter
source venv/Scripts/activate
python main.py
```

Server chạy tại: http://localhost:8000

## Bước 2: Test với HTML Demo

1. Mở file `cv_upload_demo.html` trong Chrome/Firefox
2. Kéo thả file CV.pdf vào hoặc click "Chọn file"
3. Click "📊 Phân tích CV" để xem thông tin
4. Click "💼 Tìm việc phù hợp" để nhận gợi ý công việc

## Bước 3: Test với Python

```bash
# Cài requests nếu chưa có
pip install requests

# Test với CV của bạn
python test_cv_upload.py path/to/your/cv.pdf 10
```

## API Endpoints

### 1. Phân tích CV

```bash
curl -X POST "http://localhost:8000/api/cv/upload" \
  -F "file=@your_cv.pdf"
```

### 2. Tìm việc từ CV

```bash
curl -X POST "http://localhost:8000/api/cv/recommend-jobs?top_k=10" \
  -F "file=@your_cv.pdf"
```

### 3. Test endpoint

```bash
curl http://localhost:8000/api/cv/test
```

## Frontend Example (JavaScript)

```javascript
// Upload CV và nhận gợi ý
const uploadCV = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    "http://localhost:8000/api/cv/recommend-jobs?top_k=10",
    { method: "POST", body: formData }
  );

  const data = await response.json();
  console.log("Jobs:", data.jobs);
  console.log("CV Summary:", data.cv_summary);
};

// Sử dụng
document.getElementById("fileInput").addEventListener("change", (e) => {
  uploadCV(e.target.files[0]);
});
```

## Kết quả mẫu

```json
{
  "success": true,
  "jobs": [
    {
      "job_id": "123",
      "description": "Backend Developer Python tại Hà Nội...",
      "relevance_score": 0.876
    }
  ],
  "total": 10,
  "cv_summary": {
    "skills": ["Python", "Java", "React", "Docker"],
    "experience_years": 3,
    "email": "yourname@email.com",
    "phone": "0123456789"
  }
}
```

## Troubleshooting

**Lỗi 401 "User not found"**

- Đây là lỗi của chat endpoint, không liên quan CV upload
- Kiểm tra OPENROUTER_API_KEY trong .env

**Lỗi "Không tìm thấy công việc"**

- Vector DB chưa có data
- Chạy: `python scripts/import_jobs_from_db.py`
- Chọn option 2 để import jobs

**Lỗi CORS khi test HTML**

- Đảm bảo server đang chạy
- Kiểm tra `allowed_origins` trong config.py

## Tài liệu chi tiết

- `CV_UPLOAD_GUIDE.md` - Hướng dẫn đầy đủ
- `CV_FEATURE_COMPLETED.md` - Chi tiết implementation
- `test_cv_upload.py` - Script test
- `cv_upload_demo.html` - Demo interface
