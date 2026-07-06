from openai import OpenAI
from config import settings


class OpenAIEngine:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            self.client = None
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def is_configured(self):
        return self.client is not None

    def generate_business_answer(self, system_prompt: str, user_prompt: str):
        if not self.client:
            return {
                "error": "OpenAI non configurato. Inserisci OPENAI_API_KEY."
            }

        response = self.client.responses.create(
            model=settings.OPENAI_MODEL,
            input=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        return {
            "answer": response.output_text
        }


openai_engine = OpenAIEngine()