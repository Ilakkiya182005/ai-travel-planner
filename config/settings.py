import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (explicitly from project root)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Get API keys from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or GROQ_API_KEY  # Use Groq as fallback

if not GROQ_API_KEY and not OPENAI_API_KEY:
    raise ValueError(
        "❌ No API key found! Please:\n"
        "1. Go to https://console.groq.com\n"
        "2. Generate a new API key\n"
        "3. Add it to .env file: GROQ_API_KEY=your_key_here"
    )