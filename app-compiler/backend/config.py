import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

BIG_MODEL = "llama-3.3-70b-versatile"
SMALL_MODEL = "llama-3.1-8b-instant"

MAX_REPAIR_ATTEMPTS = 3