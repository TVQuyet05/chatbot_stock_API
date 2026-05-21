"""
Cấu hình chung cho RAG Chatbot Chứng Khoán Việt Nam.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# MILVUS CONFIGURATION
# ============================================
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
MILVUS_COLLECTION = os.getenv("MILVUS_COLLECTION", "vietnam_securities_law")
MILVUS_URI = f"http://{MILVUS_HOST}:{MILVUS_PORT}"

# ============================================
# EMBEDDING CONFIGURATION
# ============================================
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "bkai-foundation-models/vietnamese-bi-encoder"
)
EMBEDDING_DIMENSION = 768  # Dimension của vietnamese-bi-encoder

# ============================================
# CHUNKING CONFIGURATION
# ============================================
# Chunk size tối đa (tính theo ký tự) khi Điều quá dài
MAX_CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

# ============================================
# DATA PATHS
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.getenv(
    "KNOWLEDGE_DIR",
    os.path.join(BASE_DIR, "datasets", "ViSecQA", "knowledge")
)

# ============================================
# RETRIEVAL CONFIGURATION
# ============================================
TOP_K = 5  # Số lượng chunks trả về khi search
SCORE_THRESHOLD = 0.5  # Ngưỡng similarity tối thiểu

# ============================================
# GEMINI CONFIGURATION (thêm API key sau)
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
