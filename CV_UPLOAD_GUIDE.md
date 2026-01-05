# Hướng dẫn sử dụng chức năng Upload CV

## 🎯 Tính năng

Server hiện có 2 endpoint mới để xử lý CV:

### 1. **Phân tích CV** (`POST /api/cv/upload`)

Upload file CV PDF và nhận thông tin phân tích:

- Email
- Số điện thoại
- Danh sách kỹ năng
- Số năm kinh nghiệm

### 2. **Gợi ý công việc từ CV** (`POST /api/cv/recommend-jobs`)

Upload file CV PDF và nhận danh sách công việc phù hợp dựa trên:

- Kỹ năng trong CV
- Kinh nghiệm làm việc
- Vector similarity search

---

## 📋 Cách sử dụng

### Test endpoint (kiểm tra service)

```bash
curl http://localhost:8000/api/cv/test
```

### 1. Upload và phân tích CV

**Curl:**

```bash
curl -X POST "http://localhost:8000/api/cv/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/cv.pdf"
```

**Python:**

```python
import requests

url = "http://localhost:8000/api/cv/upload"
files = {"file": open("my_cv.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Response:**

```json
{
  "success": true,
  "email": "your.email@example.com",
  "phone": "0123456789",
  "skills": ["Python", "Java", "React", "Docker", "AWS"],
  "experience_years": 3,
  "message": "Phân tích CV thành công"
}
```

---

### 2. Upload CV và nhận gợi ý công việc

**Curl:**

```bash
curl -X POST "http://localhost:8000/api/cv/recommend-jobs?top_k=10" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/cv.pdf"
```

**Python:**

```python
import requests

url = "http://localhost:8000/api/cv/recommend-jobs"
params = {"top_k": 10}  # Số lượng công việc muốn gợi ý
files = {"file": open("my_cv.pdf", "rb")}

response = requests.post(url, params=params, files=files)
result = response.json()

print(f"Tìm thấy {result['total']} công việc phù hợp:")
for job in result['jobs']:
    print(f"- Job ID: {job['job_id']}")
    print(f"  Độ phù hợp: {job['relevance_score']}")
    print(f"  Mô tả: {job['description'][:100]}...")
```

**Response:**

```json
{
  "success": true,
  "jobs": [
    {
      "job_id": "123",
      "description": "Backend Developer với Python và Django...",
      "relevance_score": 0.876
    },
    {
      "job_id": "456",
      "description": "Full Stack Developer cần kỹ năng React và Node.js...",
      "relevance_score": 0.823
    }
  ],
  "total": 10,
  "cv_summary": {
    "skills": ["Python", "Java", "React"],
    "experience_years": 3,
    "email": "your.email@example.com",
    "phone": "0123456789"
  },
  "message": "Tìm thấy 10 công việc phù hợp với CV của bạn"
}
```

---

## 🧪 Test với Postman/Thunder Client

1. **Method**: POST
2. **URL**: `http://localhost:8000/api/cv/recommend-jobs?top_k=10`
3. **Headers**:
   - Content-Type: multipart/form-data
4. **Body**:
   - Type: form-data
   - Key: `file`
   - Value: Chọn file PDF CV của bạn

---

## 🎨 Frontend Integration (React/Angular example)

```javascript
// Upload CV và nhận gợi ý công việc
async function uploadCVAndGetJobs(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(
      "http://localhost:8000/api/cv/recommend-jobs?top_k=10",
      {
        method: "POST",
        body: formData,
      }
    );

    const data = await response.json();

    if (data.success) {
      console.log("CV Summary:", data.cv_summary);
      console.log("Recommended jobs:", data.jobs);
      return data;
    } else {
      console.error("Error:", data.message);
    }
  } catch (error) {
    console.error("Upload error:", error);
  }
}

// Sử dụng trong component
<input
  type="file"
  accept=".pdf"
  onChange={(e) => uploadCVAndGetJobs(e.target.files[0])}
/>;
```

---

## 📊 Cách hoạt động

1. **Upload PDF**: User upload file CV.pdf
2. **Extract Text**: Server đọc và trích xuất text từ PDF
3. **Analyze CV**: Phân tích để lấy:
   - Email, phone
   - Kỹ năng (Python, Java, React...)
   - Kinh nghiệm (số năm)
4. **Create Query**: Tạo query tìm kiếm dựa trên kỹ năng và kinh nghiệm
5. **Vector Search**: Tìm công việc phù hợp trong vector database
6. **Ranking**: Sắp xếp theo độ phù hợp (relevance score)

---

## ⚙️ Cấu hình

- **Max file size**: Phụ thuộc vào FastAPI config (mặc định: 2MB)
- **Top K jobs**: 1-50 công việc (default: 10)
- **Supported format**: Chỉ PDF

---

## 🔧 Troubleshooting

**Lỗi: "Chỉ chấp nhận file PDF"**

- Đảm bảo file có extension .pdf

**Lỗi: "CV quá ngắn hoặc không đọc được"**

- File PDF có thể bị corrupt hoặc là ảnh scan
- Thử với file PDF khác có text layer

**Không tìm thấy công việc phù hợp**

- Kiểm tra vector database đã có dữ liệu chưa
- Chạy script import_jobs_from_db.py để import công việc

---

## 📝 Notes

- Service tự động phát hiện kỹ năng phổ biến trong IT
- Có thể mở rộng danh sách kỹ năng trong `cv_service.py`
- Vector search sử dụng ChromaDB embedding mặc định
- Relevance score càng cao = công việc càng phù hợp
