import json
import re
from groq import Groq
from groq import AuthenticationError
from config.settings import GROQ_API_KEY
class IntentService:
    def __init__(self, api_key):
        self.client = Groq(api_key=GROQ_API_KEY)

    def extract_params(self, user_message):
        prompt = f"""
        Extract travel parameters from this message: "{user_message}"
        Return ONLY a JSON object with these keys: 
        "source", "dest", "days", "budget", "preferences"
        
        If a value is missing, use null.
        Example: {{"source": "Delhi", "dest": "Mumbai", "days": 3, "budget": 25000, "preferences": "nature"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3-32b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
        except AuthenticationError as e:
            raise ValueError(
                "❌ AUTHENTICATION FAILED!"
            ) from e
        
        content = response.choices[0].message.content
        # Remove <think> tags and everything inside them
        clean_content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        try:
            return json.loads(clean_content)
        except json.JSONDecodeError:
            # Fallback: if there's still text outside the JSON, try to find the first '{' and last '}'
            match = re.search(r'(\{.*\})', clean_content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Failed to parse JSON from model output: {clean_content}")