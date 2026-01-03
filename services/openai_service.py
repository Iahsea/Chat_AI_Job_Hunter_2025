"""
Service xử lý logic gọi OpenAI API
"""
from openai import OpenAI
from typing import List, Dict
from config import get_settings, SYSTEM_PROMPT
from services.vector_service import search_jobs_vector


class OpenAIService:
    """Service để tương tác với OpenAI API"""
    
    def __init__(self):
        """Khởi tạo OpenAI client"""
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.ai_model if settings.ai_model.startswith("gpt") else "gpt-3.5-turbo"
        self.temperature = settings.ai_temperature
        self.max_tokens = settings.ai_max_tokens
        print(f"✅ OpenAI initialized (model: {self.model}, max tokens: {self.max_tokens})")
    
    def build_messages(
        self, 
        message: str, 
        conversation_history: List[Dict],
        jobs_info: str = ""
    ) -> List[Dict]:
        """
        Xây dựng danh sách messages cho OpenAI API
        
        Args:
            message: Tin nhắn hiện tại từ user
            conversation_history: Lịch sử hội thoại trước đó
            jobs_info: Thông tin công việc từ vector search
            
        Returns:
            List[Dict]: Danh sách messages để gửi cho OpenAI
        """
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Thêm thông tin công việc vào system message nếu có
        if jobs_info:
            messages.append({
                "role": "system",
                "content": f"Các công việc phù hợp từ hệ thống:\n{jobs_info}"
            })
        else:
            messages.append({
                "role": "system",
                "content": "Lưu ý: Hiện tại chưa tìm thấy công việc cụ thể trong cơ sở dữ liệu. Hãy tư vấn chung hoặc hỏi thêm thông tin."
            })
        
        # Thêm lịch sử hội thoại
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Thêm tin nhắn hiện tại
        messages.append({"role": "user", "content": message})
        
        return messages
    
    def generate_response(self, messages: List[Dict]) -> str:
        """
        Gọi OpenAI API để tạo response
        
        Args:
            messages: Danh sách messages
            
        Returns:
            str: Response từ AI
            
        Raises:
            Exception: Nếu có lỗi khi gọi API
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=30
        )
        return response.choices[0].message.content
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Method chính để chat với AI
        
        Args:
            message: Tin nhắn từ user
            conversation_history: Lịch sử hội thoại (optional)
            
        Returns:
            str: Response từ AI
        """
        if conversation_history is None:
            conversation_history = []
        
        # Giới hạn lịch sử chỉ giữ 5 tin nhắn gần nhất để tránh prompt quá dài
        conversation_history = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history

        # Truy xuất công việc bằng vector search (chỉ lấy top 3 job liên quan nhất)
        jobs = search_jobs_vector(message, top_k=3)
        jobs_info = "\n".join([f"- {job}" for job in jobs]) if jobs else ""
        
        # Xây dựng messages
        messages = self.build_messages(message, conversation_history, jobs_info)
        
        # Debug log (optional)
        print("\n" + "=" * 50)
        print("📝 Messages sent to OpenAI:")
        for msg in messages:
            print(f"{msg['role']}: {msg['content'][:100]}...")
        print("=" * 50)
        
        # Gọi API
        ai_response = self.generate_response(messages)
        
        # Debug log
        print("\n🤖 OpenAI Response:")
        print(ai_response)
        print("=" * 50 + "\n")
        
        return ai_response


# Singleton instance
_openai_service = None

def get_openai_service() -> OpenAIService:
    """
    Lấy instance của OpenAIService (singleton pattern)
    """
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
