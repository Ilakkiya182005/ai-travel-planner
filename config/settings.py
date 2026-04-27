import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or GROQ_API_KEY  # Use Groq as fallback
DEBUG_MODE = True
if not GROQ_API_KEY and not OPENAI_API_KEY:
    raise ValueError(
        "No API key found"
    )
