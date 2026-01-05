# AI JobHunter Chatbot

Chatbot AI hỗ trợ tìm kiếm việc làm thông minh với **RAG (Retrieval-Augmented Generation)**, được xây dựng bằng **FastAPI**, **ChromaDB** và hỗ trợ nhiều AI providers.

## ✨ Tính năng

- 🤖 **Đa AI Provider**: Hỗ trợ Google Gemini, OpenAI, và OpenRouter (miễn phí)
- 🔍 **Semantic Search**: Tìm kiếm công việc thông minh bằng ChromaDB vector database
- 💬 **RAG Pipeline**: Kết hợp vector search với AI để tư vấn việc làm chính xác
- 📊 **Import Jobs**: Import và vector hóa công việc từ MySQL database
- 🔄 **Hot-swap AI**: Chuyển đổi AI provider không cần sửa code
- 📄 **CV Upload**: Upload CV PDF và nhận gợi ý công việc phù hợp (MỚI!)

## 🚀 Cài đặt

### 1. Cài đặt dependencies

```bash
# Tạo virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac

# Cài đặt thư viện
pip install -r requirements.txt
```

### 2. Cấu hình Database

Tạo database MySQL:

```sql
CREATE DATABASE jobhunter;
```

### 3. Cấu hình AI Provider

Tạo file `.env` với nội dung:

```env
# Google Gemini API Key (Miễn phí với quota hàng ngày)
# Lấy tại: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_key_here

# OpenAI API Key (Trả phí)
# Lấy tại: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_key_here

# OpenRouter API Key (Miễn phí với nhiều models)
# Lấy tại: https://openrouter.ai/keys
OPENROUTER_API_KEY=your_openrouter_key_here

# Chọn AI provider: 'gemini', 'openai', or 'openrouter'
AI_SERVICE=openrouter

# Database config
DB_HOST=localhost
DB_PORT=3306
DB_NAME=jobhunter
DB_USER=root
DB_PASSWORD=your_password
```

**Lựa chọn AI Provider:**

| Provider          | Miễn phí   | Model                       | Ưu điểm                         |
| ----------------- | ---------- | --------------------------- | ------------------------------- |
| **OpenRouter**    | ✅ Yes     | `xiaomi/mimo-v2-flash:free` | Miễn phí hoàn toàn, nhiều model |
| **Google Gemini** | ⚠️ Limited | `gemini-3-flash-preview`    | Quota miễn phí hàng ngày        |
| **OpenAI**        | ❌ No      | `gpt-3.5-turbo`, `gpt-4`    | Chất lượng cao nhất             |

**Khuyến nghị**: Dùng **OpenRouter** cho development miễn phí!

## 🏃 Chạy ứng dụng

### 1. Kích hoạt virtual environment

```bash
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Linux/Mac
```

### 2. Import jobs vào vector database (Lần đầu tiên)

```bash
python scripts/import_jobs_from_db.py
```

Script này sẽ:

- Đọc jobs từ MySQL database
- Tạo embeddings với AI model
- Lưu vào ChromaDB vector database
- Tự động skip jobs đã tồn tại

### 3. Khởi động FastAPI server

### Cách 1: Chạy trực tiếp

```bash
python main.py
```

### Cách 2: Chạy với uvicorn

````bash
uvicorn main:app --reload

Server sẽ chạy tại: `http://localhost:8000`

### 4. Kiểm tra API


```bash
# Health check
curl http://localhost:8000/

# Test chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tìm việc Python developer", "conversation_history": []}'
````

## 📚 API Endpoints

### 1. Root - Health Check

```http
GET /
```

Response:

```json
{
  "status": "ok",
  "message": "AI JobHunter Chatbot is running!",
  "version": "1.0.0"
}
```

### 2. Health Check Detail

```http
GET /api/health
```

Response:

```json
{
  "status": "healthy",
  "gemini_configured": true
}
```

### 3. Chat với AI (RAG-powered)

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Tìm việc Python developer ở Hà Nội",
  "conversation_history": [
    {"role": "user", "content": "Xin chào"},
    {"role": "assistant", "content": "Chào bạn! Tôi có thể giúp gì?"}
  ]
}
```

Response:

```json
{
  "response": "Dựa trên tìm kiếm của bạn, tôi tìm thấy các công việc Python Developer phù hợp tại Hà Nội:\n\n1. Python Backend Developer - Công ty ABC...",
  "success": true
}
```

**Lưu ý**:

- API tự động tìm kiếm jobs phù hợp từ vector database
- Kết hợp context từ ChromaDB với AI để trả lời chính xác
- Hỗ trợ conversation history để chat liên tục

## 🔗 Tích hợp với Angular

### Service (chatbot.service.ts)

```typescript
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class ChatbotService {
  private apiUrl = "http://localhost:8000/api";

  constructor(private http: HttpClient) {}

  sendMessage(message: string, history: any[] = []): Observable<any> {
    return this.http.post(`${this.apiUrl}/chat`, {
      message: message,
      conversation_history: history,
    });
  }
}
```

### Component (chatbot.component.ts)

```typescript
import { Component } from "@angular/core";
import { ChatbotService } from "./chatbot.service";

@Component({
  selector: "app-chatbot",
  templateUrl: "./chatbot.component.html",
})
export class ChatbotComponent {
  messages: any[] = [];
  userMessage: string = "";

  constructor(private chatbotService: ChatbotService) {}

  sendMessage() {
    if (!this.userMessage.trim()) return;

    // Thêm tin nhắn user
    this.messages.push({ role: "user", content: this.userMessage });

    // Gọi API chatbot
    this.chatbotService.sendMessage(this.userMessage, this.messages).subscribe({
      next: (response) => {
        this.messages.push({ role: "assistant", content: response.response });
      },
      error: (error) => {
        console.error("Error:", error);
      },
    });

    this.userMessage = "";
  }
}
```

## 🔐 Tích hợp với Spring Boot

Nếu bạn muốn Spring Boot làm proxy cho chatbot (để thống nhất authentication):

### � Cấu trúc dự án

```
AIJobHunter/
├── main.py                 # FastAPI application entry point
├── config.py               # Settings và environment config
├── models.py               # Pydantic models cho request/response
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (không commit)
├── routes/
│   ├── __init__.py
│   └── chat.py            # Chat API endpoints
├── services/
│   ├── __init__.py
│   ├── gemini_service.py  # Google Gemini integration
│   ├── openai_service.py  # OpenAI integration
│   ├── openrouter_service.py  # OpenRouter integration
│   └── vector_service.py  # ChromaDB vector operations
├── scripts/
│   └── import_jobs_from_db.py  # Import jobs script
└── chroma_db/             # ChromaDB persistent storage (auto-created)
```

## 🎯 Workflow: Cách hệ thống hoạt động

1. **User gửi câu hỏi** → FastAPI nhận request
2. **Vector Search** → Tìm top 3 jobs liên quan từ ChromaDB
3. **Build Context** → Kết hợp jobs info + conversation history
4. **AI Generation** → Gọi AI provider (Gemini/OpenAI/OpenRouter)
5. **Response** → Trả về câu trả lời dựa trên context thực tế

## 📝 LTùy chỉnh và mở rộng

### Chuyển đổi AI Provider

Chỉ cần sửa file `.env`:

```env
# Dùng OpenRouter miễn phí
AI_SERVICE=openrouter

# Hoặc dùng Gemini
AI_SERVICE=gemini

# Hoặc dùng OpenAI
AI_SERVICE=openai
```

Sau đó restart server. **Không cần sửa code!**

### Tùy chỉnh AI behavior

Sửa trong `config.py`:

```python
SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh..."""  # Custom prompt
ai_temperature = 0.7  # Creativity (0-1)
ai_max_tokens = 800   # Response length
```

### Thay đổi model

Sửa trong `config.py` hoặc `.env`:

```python
# Gemini models
ai_model = "gemini-3-flash-preview"
ai_model = "gemini-1.5-pro-latest"

# OpenAI models
ai_model = "gpt-3.5-turbo"
ai_model = "gpt-4"

# OpenRouter free models
ai_model = "xiaomi/mimo-v2-flash:free"
ai_model = "mistral/mistral-7b-instruct:free"
```

### Tùy chỉnh Vector Search

Trong `services/vector_service.py`:

```python
# Thay đổi số lượng kết quả
jobs = search_jobs_vector(message, top_k=5)  # Default: 3

# Thay đổi embedding model
# Sửa trong import_jobs_from_db.py
```

### Thêm tính năng

**1. Lưu lịch sử chat:**

- Tích hợp PostgreSQL/MongoDB
- Lưu conversation theo user_id

**2. Authentication:**

- JWT token verification
- Rate limiting per user
- User preferences

**3. Advanced Search:**

- Filter by location, salary, experience
- Bookmark/save jobs
- Job recommendations

## 🐛 Troubleshooting

### Lỗi: `ModuleNotFoundError: No module named 'fastapi'`

```bash
pip install -r requirements.txt
```

### Lỗi: `Extra inputs are not permitted [openrouter_api_key]`

Kiểm tra `config.py` có khai báo:

```python
OPENROUTER_API_KEY: str = ""
```

### Lỗi: `Connection refused` khi gọi API

- Đảm bảo server đang chạy: `uvicorn main:app --reload`
- Kiểm tra port đúng: `http://localhost:8000`

### Không thấy jobs trong vector search

```bash
# Re-import jobs
python scripts/import_jobs_from_db.py
```

## 📊 Xem Usage/Quota

- **OpenRouter**: https://openrouter.ai/activity
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **OpenAI**: https://platform.openai.com/usage

## 🤝 Đóng góp

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

---

**Phát triển bởi**: AI JobHunter Team  
**Năm**: 2025-2026
@PostMapping("/chat")
public ResponseEntity<?> chat(@RequestBody ChatRequest request) {
// Có thể thêm authentication check ở đây

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<ChatRequest> entity = new HttpEntity<>(request, headers);

        return restTemplate.postForEntity(CHATBOT_URL, entity, ChatResponse.class);
    }

}

```

## 📝 Lưu ý

1. **CORS**: Đã cấu hình cho phép Angular (localhost:4200) gọi API
2. **API Key**: Không commit file `.env` lên Git (đã có trong `.gitignore`)
3. **Rate Limit**: OpenAI có giới hạn request, cân nhắc cache hoặc rate limiting
4. **Production**: Thay đổi `allow_origins` khi deploy production

## 🛠️ Mở rộng

### Thêm tính năng lưu lịch sử chat

- Tích hợp database (PostgreSQL, MongoDB)
- Lưu conversation history theo user_id

### Tùy chỉnh AI behavior

- Sửa `SYSTEM_PROMPT` trong `main.py`
- Thay đổi model: `gpt-4` cho kết quả tốt hơn
- Điều chỉnh `temperature` và `max_tokens`

### Thêm authentication

- JWT token verification
- Rate limiting per user
# Chat_AI_Job_Hunter_2025
```
