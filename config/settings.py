import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or GROQ_API_KEY  # Use Groq as fallback

if not GROQ_API_KEY and not OPENAI_API_KEY:
    raise ValueError("No API key found! Set GROQ_API_KEY or OPENAI_API_KEY in .env file")