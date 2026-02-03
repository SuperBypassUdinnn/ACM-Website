"""
FastAPI Dependencies

Reusable dependency functions for authentication and authorization.
"""

import uuid as uuid_lib
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Dict
from backend.config import SECRET_KEY, ALGORITHM
from backend.database import get_db_pool
from collections import defaultdict, deque
import time

# Security
security = HTTPBearer()

# Rate limiting store (in-memory)
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


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    db_pool = get_db_pool()
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


async def verify_api_key(x_api_key: str = Header(...)) -> Dict:
    """Verify API key and return client info"""
    db_pool = get_db_pool()
    
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
