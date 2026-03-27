import os
from dotenv import load_dotenv
load_dotenv()

# Job Search Configuration
SEARCH_KEYWORDS = [
    "AI Engineer",
    "Gen AI Developer",
    "ML Engineer"
]

SEARCH_LOCATIONS = [
    "Remote",
    "United States"
]

# Filtering Configuration
MIN_RELEVANCE_SCORE = 65  # 0-100 score from LLM
MAX_JOBS_PER_RUN = 50     # Max jobs to scrape and score per run
BLOCKED_COMPANIES = ["Revature", "Turing", "BairesDev"] # Add purely outsourced companies here

# LLM Configuration (Ollama)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3") # Can be mistral, deepseek-coder, etc.

# Database Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "jobs.db")

# Paths
RESUME_PDF_PATH = os.path.join(os.path.dirname(__file__), "LAKSHMIDHAR KOTIPALLI.pdf")
COVER_LETTERS_DIR = os.path.join(os.path.dirname(__file__), "cover_letters")

if not os.path.exists(COVER_LETTERS_DIR):
    os.makedirs(COVER_LETTERS_DIR)
