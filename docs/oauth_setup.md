# OAuth Setup Guide

## Getting OAuth Credentials

### 1. Google OAuth (Gmail Login)

**Go to:** https://console.cloud.google.com

**Steps:**

1. Create a new project or select existing
2. Go to "APIs & Services" → "Credentials"
3. Click "Create Credentials" → "OAuth 2.0 Client ID"
4. Configure OAuth consent screen if prompted
5. Application type: "Web application"
6. Authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (development)
   - `https://yourdomain.com/auth/google/callback` (production)
7. Copy `Client ID` and `Client Secret`
8. Add to `.env`:
   ```
   GOOGLE_CLIENT_ID=your-id-here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-secret-here
   ```

---

### 2. Microsoft OAuth

**Go to:** https://portal.azure.com

**Steps:**

1. Search for "App registrations"
2. Click "New registration"
3. Name: "ACM Web App"
4. Supported account types: "Accounts in any organizational directory and personal Microsoft accounts"
5. Redirect URI: Web → `http://localhost:8000/auth/microsoft/callback`
6. Click "Register"
7. Copy "Application (client) ID"
8. Go to "Certificates & secrets" → "New client secret"
9. Copy the secret value (show only once!)
10. Add to `.env`:
    ```
    MICROSOFT_CLIENT_ID=your-client-id-here
    MICROSOFT_CLIENT_SECRET=your-client-secret-here
    ```

---

### 3. GitHub OAuth

**Go to:** https://github.com/settings/developers

**Steps:**

1. Click "OAuth Apps" → "New OAuth App"
2. Application name: "ACM Web App"
3. Homepage URL: `http://localhost:3000`
4. Authorization callback URL: `http://localhost:8000/auth/github/callback`
5. Click "Register application"
6. Copy "Client ID"
7. Click "Generate a new client secret"
8. Copy the secret
9. Add to `.env`:
   ```
   GITHUB_CLIENT_ID=your-client-id-here
   GITHUB_CLIENT_SECRET=your-client-secret-here
   ```

---

## Testing OAuth

### Local Testing

1. Make sure `.env` has all OAuth credentials
2. Restart backend: `uvicorn app:app --reload`
3. Test OAuth URLs:
   - Google: http://localhost:8000/auth/google/login
   - Microsoft: http://localhost:8000/auth/microsoft/login
   - GitHub: http://localhost:8000/auth/github/login

### Expected Flow

1. Click OAuth login button
2. Redirected to provider (Google/Microsoft/GitHub)
3. User authorizes app
4. Redirected back to callback URL
5. User created/logged in
6. JWT token created
7. Redirected to frontend with token

---

## Production Setup

**Update redirect URIs** in each OAuth provider dashboard:

- Google: Add `https://yourdomain.com/auth/google/callback`
- Microsoft: Add `https://yourdomain.com/auth/microsoft/callback`
- GitHub: Add `https://yourdomain.com/auth/github/callback`

**Update `.env`:**

```
APP_URL=https://yourdomain.com
FRONTEND_URL=https://yourdomain.com
```
