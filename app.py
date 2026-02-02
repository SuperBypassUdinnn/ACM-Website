import time
import os
import requests
import chromadb
import asyncpg
import uuid as uuid_lib

from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Security
security = HTTPBearer()

# ======================
# CONFIG
# ======================

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/api/generate"
MODEL = "llama3.2:3b"

# Database config
DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "acm_ai"),
    "user": os.getenv("DATABASE_USER", "acm_ai"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
}

# ======================
# DATABASE POOL
# ======================

db_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for database connection pool"""
    global db_pool
    print("🔌 Connecting to database...")
    db_pool = await asyncpg.create_pool(**DB_CONFIG, min_size=2, max_size=10)
    print("✅ Database pool created")
    yield
    print("🔌 Closing database pool...")
    await db_pool.close()
    print("✅ Database pool closed")


# ======================
# APP
# ======================

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# RATE LIMIT (in-memory fallback)
# ======================

rate_limit_store = defaultdict(deque)


async def check_rate_limit(api_key: str, limit: int):
    """Check rate limiting for API key"""
    now = time.time()
    window = rate_limit_store[api_key]

    # Remove old entries outside 60 second window
    while window and window[0] <= now - 60:
        window.popleft()

    if len(window) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    window.append(now)


# ======================
# AUTHENTICATION HELPERS
# ======================


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    # Get user from database
    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, email, role FROM users WHERE id = $1",
            uuid_lib.UUID(user_id)
        )
        
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return dict(user)


# ======================
# DATABASE HELPERS
# ======================


async def verify_api_key(x_api_key: str) -> dict:
    """Verify API key and return client info"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT 
                ak.client_id,
                ak.rate_limit_per_minute,
                c.name as client_name,
                c.plan,
                c.status
            FROM api_keys ak
            JOIN clients c ON ak.client_id = c.id
            WHERE ak.key_hash = $1
              AND ak.is_active = true
              AND (ak.expires_at IS NULL OR ak.expires_at > NOW())
              AND c.status = 'active'
        """,
            x_api_key,
        )

        if not row:
            raise HTTPException(status_code=401, detail="Invalid or expired API key")

        return {
            "client_id": row["client_id"],
            "client_name": row["client_name"],
            "rate_limit": row["rate_limit_per_minute"],
            "plan": row["plan"],
        }


async def get_or_create_session(
    session_identifier: str, client_id: uuid_lib.UUID
) -> uuid_lib.UUID:
    """Get existing session or create new one"""
    async with db_pool.acquire() as conn:
        # Try to get existing session
        session = await conn.fetchrow(
            """
            SELECT id FROM chat_sessions
            WHERE session_identifier = $1 AND client_id = $2
        """,
            session_identifier,
            client_id,
        )

        if session:
            return session["id"]

        # Create new session
        new_session = await conn.fetchrow(
            """
            INSERT INTO chat_sessions (client_id, session_identifier)
            VALUES ($1, $2)
            RETURNING id
        """,
            client_id,
            session_identifier,
        )

        return new_session["id"]


async def get_chat_history(session_id: uuid_lib.UUID, limit: int = 5) -> list:
    """Get recent chat history for session"""
    async with db_pool.acquire() as conn:
        messages = await conn.fetch(
            """
            SELECT role, content
            FROM chat_messages
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """,
            session_id,
            limit,
        )

        # Return in chronological order (oldest first)
        return list(reversed(messages))


async def save_message(
    session_id: uuid_lib.UUID, role: str, content: str, token_count: int = 0
):
    """Save message to database"""
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, token_count)
            VALUES ($1, $2, $3, $4)
        """,
            session_id,
            role,
            content,
            token_count,
        )


async def log_usage(
    client_id: uuid_lib.UUID,
    api_key: str,
    endpoint: str,
    tokens_in: int,
    tokens_out: int,
):
    """Log API usage for analytics"""
    async with db_pool.acquire() as conn:
        # Get api_key_id from key_hash
        api_key_row = await conn.fetchrow(
            "SELECT client_id FROM api_keys WHERE key_hash = $1", api_key
        )

        if api_key_row:
            await conn.execute(
                """
                INSERT INTO usage_logs (client_id, api_key_id, endpoint, tokens_in, tokens_out)
                VALUES ($1, (SELECT client_id FROM api_keys WHERE key_hash = $2), $3, $4, $5)
            """,
                client_id,
                api_key,
                endpoint,
                tokens_in,
                tokens_out,
            )


# ======================
# SCHEMA
# ======================


class ChatReq(BaseModel):
    message: str
    session_id: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    plan: str  # 'free', 'basic', or 'pro'


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    client: dict
    api_key: str


# ======================
# SYSTEM PROMPT
# ======================

SYSTEM_PROMPT = """
You are a customer service assistant for TOKO ABC.

Use the provided context to answer factual questions about TOKO ABC
(such as services, prices, policies, or product information).

If a factual question cannot be answered from the context, politely say
that you do not have that information.

For greetings, thanks, confirmations, or casual conversation,
respond naturally like a professional customer service agent,
even if the context does not contain that information.

Refuse requests that are outside your role
(e.g., programming tasks, unrelated locations, or topics not about TOKO ABC).

Use the user's language.
Tone: professional, friendly, and helpful.
"""

# ======================
# VECTOR DB
# ======================

client = chromadb.PersistentClient(path="vectordb")
collection = client.get_or_create_collection(
    name="toko_abc", metadata={"hnsw:space": "cosine"}
)


def embed(text: str):
    r = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["embedding"]


def retrieve_context(query: str, k: int = 3) -> str:
    q_emb = embed(query)
    result = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
    )

    docs_list = result.get("documents")
    if not docs_list:
        docs_list = [[]]
    first_docs = (
        docs_list[0] if isinstance(docs_list, list) and len(docs_list) > 0 else []
    )
    return "\n\n".join(first_docs) if first_docs else ""


# ======================
# LLM CALL
# ======================


def call_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=120)
    r.raise_for_status()
    return r.json()["response"]


# ======================
# ENDPOINTS
# ======================


@app.post("/chat")
async def chat(req: ChatReq, x_api_key: str = Header(...)):
    """
    Main chat endpoint with database integration
    """
    # 1. Verify API key and get client info
    client_info = await verify_api_key(x_api_key)
    client_id = client_info["client_id"]

    # 2. Check rate limit
    await check_rate_limit(x_api_key, client_info["rate_limit"])

    # 3. Get or create session
    session_id = await get_or_create_session(req.session_id, client_id)

    # 4. Get chat history from database
    history = await get_chat_history(session_id, limit=5)

    # 5. Retrieve context from vector DB
    context = retrieve_context(req.message)

    # 6. Format memory block from database history
    memory_block = ""
    for h in history:
        if h["role"] == "user":
            memory_block += f"User: {h['content']}\n"
        elif h["role"] == "assistant":
            memory_block += f"Assistant: {h['content']}\n\n"

    # 7. Build prompt
    full_prompt = f"""
{SYSTEM_PROMPT}

Conversation so far:
{memory_block}

Context:
{context}

User question:
{req.message}

Answer:
"""

    # 8. Generate response
    reply = call_ollama(full_prompt).strip()

    # 9. Estimate token counts (rough estimate)
    tokens_in = len(full_prompt.split())
    tokens_out = len(reply.split())

    # 10. Save messages to database
    await save_message(session_id, "user", req.message, tokens_in)
    await save_message(session_id, "assistant", reply, tokens_out)

    # 11. Log usage
    await log_usage(client_id, x_api_key, "/chat", tokens_in, tokens_out)

    return {"reply": reply}


@app.get("/health")
async def health():
    """Health check endpoint"""
    db_status = "connected" if db_pool else "disconnected"
    return {"status": "ok", "database": db_status}


@app.get("/")
async def root():
    return {"message": "ACM AI Chatbot API", "version": "2.0"}


# ======================
# AUTHENTICATION ENDPOINTS
# ======================


@app.post("/auth/register", response_model=Token)
async def register(req: RegisterRequest):
    """
    Register new user and automatically create client + API key
    """
    async with db_pool.acquire() as conn:
        # Check if user already exists
        existing_user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", req.email
        )
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate plan
        valid_plans = ['free', 'basic', 'pro']
        if req.plan not in valid_plans:
            raise HTTPException(status_code=400, detail=f"Invalid plan. Must be one of: {valid_plans}")
        
        # Hash password
        hashed_pwd = hash_password(req.password)
        
        # Create user
        user_id = uuid_lib.uuid4()
        user = await conn.fetchrow(
            """
            INSERT INTO users (id, email, password_hash, role)
            VALUES ($1, $2, $3, 'client')
            RETURNING id, email, role
        """,
            user_id,
            req.email,
            hashed_pwd,
        )
        
        # Create client
        client_id = uuid_lib.uuid4()
        client = await conn.fetchrow(
            """
            INSERT INTO clients (id, name, plan, status)
            VALUES ($1, $2, $3, 'active')
            RETURNING id, name, plan, status
        """,
            client_id,
            req.name,
            req.plan,
        )
        
        # Link user to client
        await conn.execute(
            """
            INSERT INTO user_clients (user_id, client_id)
            VALUES ($1, $2)
        """,
            user_id,
            client_id,
        )
        
        # Generate API key
        api_key = str(uuid_lib.uuid4())
        await conn.execute(
            """
            INSERT INTO api_keys (client_id, key_hash, is_active, rate_limit_per_minute)
            VALUES ($1, $2, true, 10)
        """,
            client_id,
            api_key,
        )
        
        # Create JWT token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        return Token(
            access_token=access_token,
            user={
                "id": str(user["id"]),
                "email": user["email"],
                "role": user["role"],
            },
            client={
                "id": str(client["id"]),
                "name": client["name"],
                "plan": client["plan"],
                "status": client["status"],
            },
            api_key=api_key,
        )


@app.post("/auth/login", response_model=Token)
async def login(req: LoginRequest):
    """
    Login user and return JWT token
    """
    async with db_pool.acquire() as conn:
        # Get user
        user = await conn.fetchrow(
            "SELECT id, email, password_hash, role FROM users WHERE email = $1",
            req.email
        )
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not verify_password(req.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Get client info
        client = await conn.fetchrow(
            """
            SELECT c.id, c.name, c.plan, c.status
            FROM clients c
            JOIN user_clients uc ON c.id = uc.client_id
            WHERE uc.user_id = $1
        """,
            user["id"]
        )
        
        if not client:
            raise HTTPException(status_code=404, detail="No client found for user")
        
        # Get API key
        api_key_row = await conn.fetchrow(
            """
            SELECT key_hash FROM api_keys
            WHERE client_id = $1 AND is_active = true
            LIMIT 1
        """,
            client["id"]
        )
        
        api_key = api_key_row["key_hash"] if api_key_row else ""
        
        # Create JWT token
        access_token = create_access_token(data={"sub": str(user["id"])})
        
        return Token(
            access_token=access_token,
            user={
                "id": str(user["id"]),
                "email": user["email"],
                "role": user["role"],
            },
            client={
                "id": str(client["id"]),
                "name": client["name"],
                "plan": client["plan"],
                "status": client["status"],
            },
            api_key=api_key,
        )


@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user info from JWT token
    """
    async with db_pool.acquire() as conn:
        # Get client info
        client = await conn.fetchrow(
            """
            SELECT c.id, c.name, c.plan, c.status
            FROM clients c
            JOIN user_clients uc ON c.id = uc.client_id
            WHERE uc.user_id = $1
        """,
            uuid_lib.UUID(current_user["id"])
        )
        
        # Get API key
        api_key_row = await conn.fetchrow(
            """
            SELECT key_hash FROM api_keys
            WHERE client_id = $1 AND is_active = true
            LIMIT 1
        """,
            client["id"]
        ) if client else None
        
        return {
            "user": current_user,
            "client": dict(client) if client else None,
            "api_key": api_key_row["key_hash"] if api_key_row else None,
        }
