from .config import Settings

# API defaults
API_V1_STR = "/api/v1"
PROJECT_NAME = "RAG Chatbot"
VERSION = "0.1.0"

# CORS defaults
BACKEND_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

# Model defaults
GEMINI_MODEL = "gemini-1.5-flash"
EMBEDDING_MODEL = "models/text-embedding-004"
EMBEDDING_DIMENSIONS = 768

# Rate limits (based on Gemini API)
MAX_RPM = 12  # Buffer below 15 RPM limit for GEMINI calls
MAX_TPM = 28000  # Buffer below 32,000 TPM
MAX_CHUNK_TOKENS = 1500  # Typical chunk token limit

EMBEDDING_MAX_RPM = 1500  # Rate limit for embeddings model calls

# Document processing defaults
CHUNK_SIZE = 500  # ~300 words per chunk
CHUNK_OVERLAP = 50  # 20% overlap for context
MAX_CHUNKS_PER_DOC = 100  # Balance between completeness and rate limits
SIMILARITY_TOP_K = 3  # Balance between context and token usage
EMBEDDING_BATCH_SIZE = 5  # 5 chunks per batch
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB to handle PDFs and spreadsheets

# Chat defaults
TEMPERATURE = 0.1
MAX_TOKENS = 1000  # Response token limit
SYSTEM_PROMPT = """You are a helpful AI assistant. When answering questions:
1. Use the provided context if available
2. Acknowledge which documents you're referencing
3. For numerical data, specify the source file and relevant details
4. If analyzing spreadsheets or CSV data, explain your interpretation
5. Maintain the original formatting when quoting text"""
SIMILARITY_THRESHOLD = 0.7
MAX_HISTORY = 10

# Supported file types
SUPPORTED_FILE_TYPES = {
    'application/pdf': 'pdf',      # PDF documents (up to 5MB)
    'text/plain': 'txt',           # Text files (up to 2MB)
    'text/csv': 'csv',             # CSV data (up to 3MB)
    'application/json': 'json',     # JSON data (up to 2MB)
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx'  # Excel (up to 4MB)
}

# Logging defaults
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Initialize settings with defaults and env vars
settings = Settings(
    API_V1_STR=API_V1_STR,
    PROJECT_NAME=PROJECT_NAME,
    VERSION=VERSION,
    GEMINI_MODEL=GEMINI_MODEL,
    EMBEDDING_MODEL=EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS=EMBEDDING_DIMENSIONS,
    CHUNK_SIZE=CHUNK_SIZE,
    CHUNK_OVERLAP=CHUNK_OVERLAP,
    MAX_CHUNKS_PER_DOC=MAX_CHUNKS_PER_DOC,
    SIMILARITY_TOP_K=SIMILARITY_TOP_K,
    EMBEDDING_BATCH_SIZE=EMBEDDING_BATCH_SIZE,
    MAX_FILE_SIZE=MAX_FILE_SIZE,
    TEMPERATURE=TEMPERATURE,
    MAX_TOKENS=MAX_TOKENS,
    SYSTEM_PROMPT=SYSTEM_PROMPT,
    SIMILARITY_THRESHOLD=SIMILARITY_THRESHOLD,
    MAX_HISTORY=MAX_HISTORY,
    BACKEND_CORS_ORIGINS=BACKEND_CORS_ORIGINS,
    SUPPORTED_FILE_TYPES=SUPPORTED_FILE_TYPES,
    LOG_FORMAT=LOG_FORMAT,
    LOG_LEVEL=LOG_LEVEL,
    MAX_RPM=MAX_RPM,
    MAX_TPM=MAX_TPM,
    MAX_CHUNK_TOKENS=MAX_CHUNK_TOKENS,
    EMBEDDING_MAX_RPM=EMBEDDING_MAX_RPM
) 