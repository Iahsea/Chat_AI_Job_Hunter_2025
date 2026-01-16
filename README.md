# AI Hotel Booking Chatbot

Chatbot AI hỗ trợ tư vấn và đặt phòng khách sạn, được xây dựng bằng FastAPI và Google Gemini API.

## 🏨 Tính năng

- **Tư vấn đặt phòng**: Giúp khách hàng tìm khách sạn/phòng phù hợp với nhu cầu
- **Giải đáp thông tin**: Trả lời câu hỏi về khách sạn, loại phòng, tiện ích, chính sách
- **Hỗ trợ đặt phòng**: Hướng dẫn quy trình đặt phòng, thanh toán, hủy phòng
- **Gợi ý điểm đến**: Tư vấn các điểm du lịch, khách sạn theo mùa, theo sự kiện

## 🚀 Cài đặt

### 1. Tạo môi trường ảo

```bash
python -m venv venv

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình Google Gemini API Key

1. Tạo file `.env`:

```bash
copy .env.example .env
```

2. Lấy API key từ [Google AI Studio](https://makersuite.google.com/app/apikey)

3. Cập nhật file `.env`:

```
GEMINI_API_KEY=your_api_key_here
```

## 🏃 Chạy ứng dụng

### Cách 1: Chạy trực tiếp

```bash
python main.py
```

### Cách 2: Chạy với uvicorn

```bash
uvicorn main:app --reload
```

Server sẽ chạy tại: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

## 📚 API Endpoints

### 1. Health Check

```
GET /
```

Response:

```json
{
  "status": "ok",
  "message": "AI Hotel Booking Chatbot is running! 🏨",
  "version": "1.0.0",
  "description": "Hệ thống chatbot AI hỗ trợ tư vấn và đặt phòng khách sạn"
}
```

### 2. Chat với AI

```
POST /api/chat
Content-Type: application/json

{
  "message": "Tôi muốn đặt phòng khách sạn ở Đà Nẵng",
  "conversation_history": []
}
```

Response:

```json
{
  "response": "Tuyệt vời! Đà Nẵng có nhiều khách sạn đẹp. Bạn muốn đặt phòng cho bao nhiêu người và trong khoảng thời gian nào ạ?",
  "success": true
}
```

### 3. Health Check chi tiết

```
GET /api/health
```

Response:

```json
{
  "status": "healthy",
  "gemini_configured": true
}
```

## 🔗 Tích hợp với Angular

### Service (chatbot.service.ts)

```typescript
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  message: string;
  conversation_history: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  success: boolean;
}

@Injectable({
  providedIn: "root",
})
export class ChatbotService {
  private apiUrl = "http://localhost:8000/api";

  constructor(private http: HttpClient) {}

  chat(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat`, request);
  }

  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }
}
```

### Component (chatbot.component.ts)

```typescript
import { Component } from "@angular/core";
import { ChatbotService, ChatMessage, ChatResponse } from "./chatbot.service";

@Component({
  selector: "app-chatbot",
  template: `
    <div class="chat-container">
      <div class="messages">
        <div *ngFor="let msg of messages" [class]="msg.role">
          {{ msg.content }}
        </div>
      </div>
      <div class="input-area">
        <input
          [(ngModel)]="userInput"
          (keyup.enter)="sendMessage()"
          placeholder="Hỏi về khách sạn..."
        />
        <button (click)="sendMessage()" [disabled]="isLoading">
          {{ isLoading ? "Đang xử lý..." : "Gửi" }}
        </button>
      </div>
    </div>
  `,
})
export class ChatbotComponent {
  messages: ChatMessage[] = [];
  userInput = "";
  isLoading = false;

  constructor(private chatbotService: ChatbotService) {}

  sendMessage() {
    if (!this.userInput.trim() || this.isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: this.userInput,
    };
    this.messages.push(userMessage);
    this.isLoading = true;

    this.chatbotService
      .chat({
        message: this.userInput,
        conversation_history: this.messages.slice(0, -1),
      })
      .subscribe({
        next: (response: ChatResponse) => {
          this.messages.push({
            role: "assistant",
            content: response.response,
          });
          this.isLoading = false;
        },
        error: (err) => {
          console.error(err);
          this.isLoading = false;
        },
      });

    this.userInput = "";
  }
}
```

## 🗄️ Cơ sở dữ liệu hỗ trợ

Chatbot được thiết kế để tích hợp với hệ thống Hotel Booking System với các bảng:

- **hotels**: Thông tin khách sạn (tên, địa chỉ, rating, tiện ích)
- **room_types**: Loại phòng (Standard, Deluxe, Suite, Villa...)
- **amenities**: Tiện nghi (WiFi, điều hòa, minibar, view biển...)
- **bookings**: Đặt phòng
- **payments**: Thanh toán
- **reviews**: Đánh giá

## 📝 Ví dụ hội thoại

```
User: Xin chào
Bot: Chào bạn! 🏨 Tôi là trợ lý đặt phòng khách sạn. Tôi có thể giúp gì cho bạn hôm nay?

User: Tôi muốn đặt phòng ở Đà Nẵng cho 2 người
Bot: Tuyệt vời! Đà Nẵng là điểm đến tuyệt đẹp! 🌊 Bạn có thể cho tôi biết thêm:
- Ngày check-in và check-out?
- Ngân sách khoảng bao nhiêu/đêm?
- Bạn có yêu cầu đặc biệt nào không (view biển, gần trung tâm...)?

User: Từ 20-22/1, ngân sách khoảng 2 triệu/đêm, muốn view biển
Bot: Với yêu cầu của bạn, tôi gợi ý một số khách sạn:
1. **Grand Aurora Riverside Hotel** ⭐⭐⭐⭐
   - Phòng Deluxe River View: 1,950,000đ/đêm
   - Tiện nghi: WiFi, điều hòa, minibar, ban công view sông
2. **Ocean Blue Resort** ⭐⭐⭐⭐⭐
   - Phòng Standard Ocean View: 2,400,000đ/đêm
   - Tiện nghi: View biển trực tiếp, hồ bơi, spa

Bạn muốn tôi cung cấp thêm thông tin chi tiết về khách sạn nào?
```

## 🔧 Cấu hình nâng cao

### File config.py

```python
# AI Configuration
ai_model: str = "gemini-2.0-flash"
ai_temperature: float = 0.7
ai_max_tokens: int = 500

# CORS - Thêm domain frontend của bạn
allowed_origins: list = ["http://localhost:4200", "https://yourdomain.com"]
```

## 📄 License

MIT License
