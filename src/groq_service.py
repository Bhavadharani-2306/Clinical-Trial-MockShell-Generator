# src/groq_service.py
import os

class GroqService:
    def __init__(self):
        # Retrieve API key safely without raising a terminal-breaking error
        self.api_key = os.environ.get("GROQ_API_KEY", "")
        self.model = "llama-3.3-70b-versatile"
        self.client = None

        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
            except ImportError:
                print("Warning: 'groq' package is not installed. Run: pip install groq")

    def has_api_key(self) -> bool:
        """Helper method to check if the API key is active and ready."""
        return bool(self.api_key) and self.client is not None

    def analyze_text(self, system_prompt: str, user_content: str, response_format_json: bool = False) -> str:
        """Sends extracted text to Groq Cloud for processing safely."""
        if not self.has_api_key():
            return ""
            
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                "temperature": 0.1
            }
            
            if response_format_json:
                kwargs["response_format"] = {"type": "json_object"}

            chat_completion = self.client.chat.completions.create(**kwargs)
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            return ""