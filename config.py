"""
Cấu hình ứng dụng và environment variables
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    GEMINI_API_KEY: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS
    allowed_origins: list = ["http://localhost:4200"]
    
    # AI Configuration
    ai_model: str = "gemini-3-flash-preview"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 500
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Lấy settings singleton (cache để tránh đọc file .env nhiều lần)
    """
    return Settings(_env_file='.env')


# System prompt cho chatbot
SYSTEM_PROMPT = """Bạn là trợ lý AI thông minh của JobHunter - nền tảng tìm kiếm việc làm hàng đầu.
Nhiệm vụ của bạn:
- Hỗ trợ người dùng tìm kiếm công việc phù hợp
- Tư vấn về CV, kỹ năng, nghề nghiệp
- Giải đáp thắc mắc về việc làm, lương, phúc lợi
- Gợi ý các công việc phù hợp với kỹ năng của họ

Hãy trả lời thân thiện, chuyên nghiệp và hữu ích."""
