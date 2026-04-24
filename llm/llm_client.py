from groq import Groq, AuthenticationError
import re
from config.settings import GROQ_API_KEY
class LLMClient:
    def __init__(self, api_key):
        self.client = Groq(api_key=GROQ_API_KEY)

    def generate_itinerary(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[
                    {"role": "system", "content": "You are a professional travel agent. Plan logically and stick to the budget provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=5000
            )
        except AuthenticationError as e:
            raise ValueError(
                "API AUTHENTICATION FAILED!"
            ) from e

        content = response.choices[0].message.content
        # Remove <think> tags and everything inside them
        clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        print(f"LLMClient raw response: {clean_content}")  # Debugging line to check the raw response
        return clean_content