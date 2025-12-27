# AI JobHunter Chatbot

Chatbot AI hỗ trợ tìm kiếm việc làm, được xây dựng bằng FastAPI và OpenAI API.

## 🚀 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình OpenAI API Key

1. Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

2. Lấy API key từ [OpenAI Platform](https://platform.openai.com/api-keys)

3. Cập nhật file `.env`:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

## 🏃 Chạy ứng dụng

# Kích hoạt venv trước khi chạy

source venv/Scripts/activate

### Cách 1: Chạy trực tiếp

```bash
python main.py
```

### Cách 2: Chạy với uvicorn

```bash
uvicorn main:app --reload

```

Server sẽ chạy tại: `http://localhost:8000`

## 📚 API Endpoints

### 1. Health Check

```
GET /
```

### 2. Chat với AI

```
POST /api/chat
Content-Type: application/json

{
  "message": "Tôi muốn tìm việc lập trình viên Python",
  "conversation_history": []
}
```

Response:

```json
{
  "response": "Xin chào! Tôi có thể giúp bạn tìm việc lập trình viên Python...",
  "success": true
}
```

### 3. Health Check

```
GET /api/health
```

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

### Spring Boot Controller

```java
@RestController
@RequestMapping("/api/chatbot")
public class ChatbotController {

    private final RestTemplate restTemplate = new RestTemplate();
    private static final String CHATBOT_URL = "http://localhost:8000/api/chat";

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
