import chromadb
from chromadb.utils import embedding_functions

# Khởi tạo ChromaDB persistent client
client = chromadb.PersistentClient(path="d:/D_CNTT/TTCS/AIJobHunter/vector_db")
collection = client.get_or_create_collection("jobs")

# Hàm thêm công việc vào vector DB
def add_job_to_vector(job_id: str, job_text: str):
    collection.add(
        documents=[job_text],
        ids=[job_id]
    )

# Hàm tìm kiếm công việc theo ngữ nghĩa
def search_jobs_vector(query: str, top_k: int = 5):
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    # Trả về danh sách mô tả công việc phù hợp
    return results['documents'][0] if results['documents'] else []

def check_job_exists(job_id: str) -> bool:
    """Kiểm tra job đã tồn tại trong vector DB chưa"""
    try:
        result = collection.get(ids=[job_id])
        return len(result['ids']) > 0
    except:
        return False

def get_all_job_ids():
    """Lấy tất cả id của job đã có trong vector DB"""
    try:
        result = collection.get()
        return set(result['ids'])
    except:
        return set()