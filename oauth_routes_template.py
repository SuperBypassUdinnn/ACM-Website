# OAuth routes for social login
# Add these routes to app.py

# ======================
# OAUTH ROUTES
# ======================

@app.get('/auth/{provider}/login')
async def oauth_login(provider: str, request: Request):
    """Initiate OAuth flow with provider (google, microsoft, github)"""
    if provider not in ['google', 'microsoft', 'github']:
        raise HTTPException(status_code=400, detail="Invalid OAuth provider")
    
    # Redirect URI - where OAuth provider will send user after authentication
    redirect_uri = f"{os.getenv('APP_URL', 'http://localhost:8000')}/auth/{provider}/callback"
    
    return await oauth.create_client(provider).authorize_redirect(request, redirect_uri)


@app.get('/auth/{provider}/callback')
async def oauth_callback(provider: str, request: Request):
    """Handle OAuth callback and create/login user"""
    try:
        # Get access token from provider
        token = await oauth.create_client(provider).authorize_access_token(request)
        
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
            # GitHub needs separate API call for user info
            resp = await oauth.create_client(provider).get('https://api.github.com/user', token=token)
            user_info = resp.json()
            oauth_id = str(user_info['id'])
            
            # Get email (may need separate call if not public)
            email = user_info.get('email')
            if not email:
                email_resp = await oauth.create_client(provider).get('https://api.github.com/user/emails', token=token)
                emails = email_resp.json()
                primary_email = next((e for e in emails if e['primary']), emails[0] if emails else None)
                email = primary_email['email'] if primary_email else None
            
            name = user_info.get('name') or user_info.get('login')
            avatar = user_info.get('avatar_url')
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")
        
        # Find or create user in database
        async with db_pool.acquire() as conn:
            # Check if OAuth user exists
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE oauth_provider = $1 AND oauth_id = $2",
                provider, oauth_id
            )
            
            if not user:
                # Check if email already exists with different provider
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE email = $1",
                    email
                )
                
                if user:
                    # Link OAuth to existing account
                    await conn.execute(
                        """
                        UPDATE users 
                        SET oauth_provider = $1, oauth_id = $2, avatar_url = $3, email_verified = TRUE
                        WHERE id = $4
                        """,
                        provider, oauth_id, avatar, user['id']
                    )
                    # Refresh user data
                    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user['id'])
                else:
                    # Create new user
                    user_id = uuid_lib.uuid4()
                    await conn.execute(
                        """
                        INSERT INTO users (id, email, name, oauth_provider, oauth_id, avatar_url, email_verified, role)
                        VALUES ($1, $2, $3, $4, $5, $6, TRUE, 'user')
                        """,
                        user_id, email, name, provider, oauth_id, avatar
                    )
                    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": str(user['id']), "email": user['email']}
        )
        
        # Redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}&provider={provider}"
        )
        
    except Exception as e:
        print(f"OAuth error: {e}")
        import traceback
        traceback.print_exc()
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return RedirectResponse(
            url=f"{frontend_url}/login?error=oauth_failed&message={str(e)}"
        )
