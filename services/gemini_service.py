"""
Service xử lý logic gọi Google Gemini API
"""
import google.generativeai as genai
from typing import List, Dict
from config import get_settings, SYSTEM_PROMPT
from services.vector_service import search_jobs_vector



class GeminiService:
    """Service để tương tác với Google Gemini API"""
    
    def __init__(self):
        """Khởi tạo Gemini client"""
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Cấu hình generation với giới hạn token
        generation_config = {
            "temperature": settings.ai_temperature,
            "max_output_tokens": settings.ai_max_tokens,  # Giới hạn output
            "top_p": 0.95,
        }
        
        self.model = genai.GenerativeModel(
            settings.ai_model,
            generation_config=generation_config
        )
        print(f"✅ Gemini initialized (max tokens: {settings.ai_max_tokens})")
    
    def build_conversation(
        self, 
        message: str, 
        conversation_history: List[Dict],
        jobs_info: str = ""
    ) -> str:
        """
        Xây dựng chuỗi conversation từ lịch sử và tin nhắn mới
        
        Args:
            message: Tin nhắn hiện tại từ user
            conversation_history: Lịch sử hội thoại trước đó
            
        Returns:
            str: Chuỗi conversation đầy đủ để gửi cho AI
        """
        conversation = SYSTEM_PROMPT + "\n\n"

        if jobs_info:
            conversation += f"Các công việc phù hợp từ hệ thống:\n{jobs_info}\n\n"
        else:
            conversation += "Lưu ý: Hiện tại chưa tìm thấy công việc cụ thể trong cơ sở dữ liệu. Hãy tư vấn chung hoặc hỏi thêm thông tin.\n\n"
        
        # Thêm lịch sử hội thoại
        if conversation_history:
            for msg in conversation_history:
                role = "User" if msg.get("role") == "user" else "Assistant"
                conversation += f"{role}: {msg.get('content')}\n"
        
        # Thêm tin nhắn hiện tại
        conversation += f"User: {message}\nAssistant:"
        
        return conversation
    
    def generate_response(self, conversation: str) -> str:
        """
        Gọi Gemini API để tạo response
        
        Args:
            conversation: Chuỗi conversation đầy đủ
            
        Returns:
            str: Response từ AI
            
        Raises:
            Exception: Nếu có lỗi khi gọi API
        """
        # Thêm timeout 30s để tránh request bị treo
        response = self.model.generate_content(
            conversation,
            request_options={"timeout": 30}
        )
        return response.text
    
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
        
        # Xây dựng conversation
        conversation = self.build_conversation(message, conversation_history, jobs_info)
        
        # Debug log (optional)
        print("\n" + "=" * 50)
        print("📝 Conversation sent to AI:")
        print(conversation)
        print("=" * 50)
        
        # Gọi API
        ai_response = self.generate_response(conversation)
        
        # Debug log
        print("\n🤖 AI Response:")
        print(ai_response)
        print("=" * 50 + "\n")
        
        return ai_response


# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """
    Lấy instance của GeminiService (singleton pattern)
    """
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
