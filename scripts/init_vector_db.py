"""
Script khởi tạo dữ liệu mẫu cho vector database
Chạy script này một lần để nạp dữ liệu công việc ban đầu vào ChromaDB
"""
from services.vector_service import add_job_to_vector

# Danh sách công việc mẫu (trong thực tế nên lấy từ database)
jobs = [
    {
        "id": "1", 
        "title": "Lập trình viên Python", 
        "description": "Phát triển ứng dụng web bằng Python/Django/Flask tại Hà Nội. Yêu cầu 1-2 năm kinh nghiệm, lương 15-20 triệu."
    },
    {
        "id": "2", 
        "title": "Data Analyst", 
        "description": "Phân tích dữ liệu, xây dựng báo cáo. Yêu cầu biết SQL, Python, Excel. Làm việc tại Hồ Chí Minh, lương 12-18 triệu."
    },
    {
        "id": "3", 
        "title": "Frontend Developer", 
        "description": "Làm việc với React, Angular, Vue.js. Xây dựng giao diện web responsive. Hà Nội, lương 12-18 triệu."
    },
    {
        "id": "4", 
        "title": "Backend Developer Java", 
        "description": "Phát triển API RESTful với Spring Boot, Microservices. Yêu cầu 2+ năm kinh nghiệm Java. Lương 18-25 triệu."
    },
    {
        "id": "5", 
        "title": "DevOps Engineer", 
        "description": "Quản lý hạ tầng AWS/Azure, CI/CD với Docker, Kubernetes, Jenkins. Lương 20-30 triệu, remote."
    },
    {
        "id": "6", 
        "title": "Mobile Developer", 
        "description": "Phát triển ứng dụng di động với React Native hoặc Flutter. Hà Nội/HCM, lương 15-22 triệu."
    },
    {
        "id": "7", 
        "title": "QA/Tester", 
        "description": "Kiểm thử phần mềm, viết test case, automation testing với Selenium. Hà Nội, lương 10-15 triệu."
    },
    {
        "id": "8", 
        "title": "Full Stack Developer", 
        "description": "Phát triển cả frontend (React) và backend (Node.js/Python). Startup công nghệ, lương 18-28 triệu."
    },
]

def init_vector_db():
    """Khởi tạo vector database với dữ liệu mẫu"""
    print("=" * 60)
    print("🚀 BẮT ĐẦU NẠP DỮ LIỆU VÀO VECTOR DATABASE")
    print("=" * 60)
    
    for job in jobs:
        try:
            text = f"{job['title']}: {job['description']}"
            add_job_to_vector(job['id'], text)
            print(f"✅ Đã thêm: [{job['id']}] {job['title']}")
        except Exception as e:
            print(f"❌ Lỗi khi thêm [{job['id']}] {job['title']}: {e}")
    
    print("=" * 60)
    print(f"🎉 HOÀN TẤT! Đã nạp {len(jobs)} công việc vào vector DB.")
    print("=" * 60)

if __name__ == "__main__":
    init_vector_db()
