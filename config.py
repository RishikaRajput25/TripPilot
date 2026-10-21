
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "TripPilot"
APP_TAGLINE = "Your journey, intelligently planned."

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

DATA_DIR = "data"
EXPORT_DIR = "exports"

DEFAULT_CURRENCY = "INR"
SUPPORTED_BUDGETS = ["Budget", "Moderate", "Luxury"]
SUPPORTED_PACES = ["Relaxed", "Moderate", "Fast-Paced"]
SUPPORTED_PARTIES = ["Solo", "Couple", "Family", "Friends"]

DEMO_MODE = not (GEMINI_API_KEY or GROQ_API_KEY)
