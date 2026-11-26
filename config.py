import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).parent
KB_DIR = BASE_DIR / "knowledge_base"
VECTOR_DIR = BASE_DIR / "vector_store"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
EMBED_MODEL = "gemini-embedding-001"

CHUNK_SIZE = 800       # max characters per chunk
CHUNK_OVERLAP = 120    # overlap between consecutive chunks
TOP_K = 4
MAX_FILE_BYTES = 200 * 1024
SUPPORTED = {".py": "python", ".java": "java"}


# ---- Milestone 2: agent thresholds & LLM ----
GEMINI_MODEL = "gemini-2.5-flash"
MAX_FUNC_LINES = 40
MAX_PARAMS = 5
MAX_COMPLEXITY = 10
MAX_NESTING = 4
MAX_CLASS_METHODS = 15
MAX_CLASS_LINES = 300
MAX_LINE_LEN = 120
