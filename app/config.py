import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from env, fallback to "changeme" if not set
API_KEY = os.getenv("API_KEY", "changeme")

# Optional: holidays set
HOLIDAYS = set(os.getenv("HOLIDAYS", "").split(",")) if os.getenv("HOLIDAYS") else set()
