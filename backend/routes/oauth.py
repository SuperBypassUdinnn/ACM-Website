"""
OAuth Routes

Social login endpoints for Google, Microsoft, and GitHub.
"""

import uuid as uuid_lib
from fastapi import APIRouter, Request, HTTPException
from starlette.responses import RedirectResponse
from backend.auth.oauth import oauth
from backend.auth.utils import create_access_token
from backend.config import APP_URL, FRONTEND_URL
from backend.database import get_db_pool

router = APIRouter(prefix="/auth")


@router.get('/{provider}/login')
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth flow"""
    if provider not in ['google', 'microsoft', 'github']:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    redirect_uri = f"{APP_URL}/auth/{provider}/callback"
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@router.get('/{provider}/callback')
async def oauth_callback(provider: str, request: Request):
    """Handle OAuth callback and create/login user"""
    try:
        token = await oauth.create_client(provider).authorize_access_token(request)
        db_pool = get_db_pool()
        
        # Extract user info based on provider
        if provider == 'google':
            user_info = token.get('userinfo')
            oauth_id = user_info['sub']
            email = user_info['email']
            name = user_info.get('name', email.split('@')[0])
            avatar = user_info.get('picture')
            
        elif provider == 'microsoft':
            user_info = token.get('userinfo')
            oauth_id = user_info['sub']
            email = user_info.get('email') or user_info.get('preferred_username')
            name = user_info.get('name', email.split('@')[0])
            avatar = None
            
        elif provider == 'github':
            resp = await oauth.create_client(provider).get('https://api.github.com/user', token=token)
            user_info = resp.json()
            oauth_id = str(user_info['id'])
            email = user_info.get('email')
            
            if not email:
                email_resp = await oauth.create_client(provider).get('https://api.github.com/user/emails', token=token)
                emails = email_resp.json()
                primary_email = next((e for e in emails if e['primary']), emails[0] if emails else None)
                email = primary_email['email'] if primary_email else None
                
            name = user_info.get('name') or user_info.get('login')
            avatar = user_info.get('avatar_url')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided")
        
        # Find or create user
        async with db_pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE oauth_provider = $1 AND oauth_id = $2",
                provider, oauth_id
            )
            
            if not user:
                user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
                
                if user:
                    # Link OAuth to existing account
                    await conn.execute(
                        "UPDATE users SET oauth_provider = $1, oauth_id = $2, avatar_url = $3, email_verified = TRUE WHERE id = $4",
                        provider, oauth_id, avatar, user['id']
                    )
                    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user['id'])
                else:
                    # Create new user
                    user_id = uuid_lib.uuid4()
                    await conn.execute(
                        "INSERT INTO users (id, email, name, oauth_provider, oauth_id, avatar_url, email_verified, role) VALUES ($1, $2, $3, $4, $5, $6, TRUE, 'user')",
                        user_id, email, name, provider, oauth_id, avatar
                    )
                    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": str(user['id']), "email": user['email']})
        
        # Redirect to frontend with token
        return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?token={access_token}&provider={provider}")
        
    except Exception as e:
        print(f"OAuth error: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=oauth_failed")
