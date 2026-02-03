"""
Backend Configuration Module

All environment variables and constants used throughout the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ======================
# API CONFIGURATION
# ======================

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/generate"
MODEL = "llama3.2:3b"

# ======================
# DATABASE CONFIGURATION
# ======================

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "acm_ai"),
    "user": os.getenv("DATABASE_USER", "acm_ai"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
}

# ======================
# JWT CONFIGURATION
# ======================

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-this")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ======================
# VECTOR DB CONFIGURATION
# ======================

VECTOR_DB_DIR = "./scripts/vectordb"

# ======================
# OAUTH URLS
# ======================

APP_URL = os.getenv('APP_URL', 'http://localhost:8000')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# ======================
# SYSTEM PROMPT
# ======================

DEFAULT_SYSTEM_PROMPT = """
You are an AI customer service assistant.
Your role is to provide helpful information about products, services, pricing, and policies based on the context provided.

Guidelines:
- ALWAYS check the provided context first before answering
- If the context contains relevant information (even partially), USE it to answer
- Be helpful, friendly, and professional

FORMATTING RULES:
- When listing multiple items, use numbered markdown lists (1., 2., 3.)
- Use **bold text** for important terms like service names, prices, or key information
- Keep paragraphs short and scannable
- Format example: "1. **Item**: Description\\n2. **Item**: Description"

IMPORTANT: 
- The context below contains information from the knowledge base
- If no relevant context is provided, politely say you don't have that information
- Never make up information that's not in the context
"""
