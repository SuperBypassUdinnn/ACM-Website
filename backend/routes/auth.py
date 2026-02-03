"""
Authentication Routes

User registration, login, and profile endpoints.
"""

import uuid as uuid_lib
from fastapi import APIRouter, HTTPException, Depends
from backend.models import RegisterRequest, LoginRequest, Token
from backend.auth.utils import hash_password, verify_password, create_access_token
from backend.dependencies import get_current_user
from backend.database import get_db_pool

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=Token)
async def register(req: RegisterRequest):
    """
    Register new user and automatically create client + API key
    """
    db_pool = get_db_pool()
    
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


@router.post("/login", response_model=Token)
async def login(req: LoginRequest):
    """
    Login user and return JWT token
    """
    db_pool = get_db_pool()
    
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


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user info from JWT token
    """
    db_pool = get_db_pool()
    
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
