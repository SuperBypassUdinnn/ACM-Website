"""
ACM AI Chatbot API - Main Application

Modular FastAPI application with clean separation of concerns.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from backend.config import SECRET_KEY
from backend.database import lifespan
from backend.routes import health, chat, auth, oauth

# ======================
# CREATE APP
# ======================

app = FastAPI(
    title="ACM AI Chatbot API",
    description="Multi-tenant RAG-powered chatbot with OAuth authentication",
    version="2.0",
    lifespan=lifespan
)

# ======================
# MIDDLEWARE
# ======================

# Session middleware for OAuth (must be before CORS)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ======================
# INCLUDE ROUTERS
# ======================

# Health checks
app.include_router(health.router, tags=["Health"])

# Chat endpoints
app.include_router(chat.router, tags=["Chat"])

# Authentication
app.include_router(auth.router, tags=["Authentication"])

# OAuth social login
app.include_router(oauth.router, tags=["OAuth"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
