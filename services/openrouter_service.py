"""
Service xử lý logic gọi OpenRouter AI API
"""
import requests
from typing import List, Dict
from config import get_settings, SYSTEM_PROMPT

class OpenRouterService:
    """Service để tương tác với OpenRouter AI"""
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.ai_model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def build_conversation(self, message: str, conversation_history: List[Dict]) -> list:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        if conversation_history:
            for msg in conversation_history:
                role = "user" if msg.get("role") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("content")})
        messages.append({"role": "user", "content": message})
        return messages

    def generate_response(self, conversation: list) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": conversation
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            print("[OpenRouterService] Request payload:", payload)
            print("[OpenRouterService] Response status:", response.status_code)
            print("[OpenRouterService] Response text:", response.text)
            if response.status_code == 200:
                data = response.json()
                if data.get("choices") and data["choices"][0].get("message"):
                    return data["choices"][0]["message"]["content"]
                return "Không nhận được phản hồi từ AI."
            return f"Lỗi gọi OpenRouter: {response.status_code} - {response.text}"
        except Exception as e:
            print(f"[OpenRouterService] Exception: {e}")
            return f"Lỗi gọi OpenRouter: {str(e)}"

    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        if conversation_history is None:
            conversation_history = []
        conversation = self.build_conversation(message, conversation_history)
        return self.generate_response(conversation)

# Singleton instance
_openrouter_service = None

def get_openrouter_service() -> OpenRouterService:
    global _openrouter_service
    if _openrouter_service is None:
        _openrouter_service = OpenRouterService()
    return _openrouter_service
