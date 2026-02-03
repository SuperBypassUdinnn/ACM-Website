"""Quick register test user without seeding full database"""
import asyncio
import asyncpg
import uuid
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "acm_ai"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "postgres"),
}

async def quick_register():
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Use fixed UUIDs for test data
        user_id = "43010f4c-ebbd-4edf-b6c9-ea2805ab74a1"
        client_id = "43010f4c-ebbd-4edf-b6c9-ea2805ab74a1"
        api_key = str(uuid.uuid4())
        # Pre-hashed "test123" password
        hashed_password = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Z1aafU3.kcKuQUjiq"
        
        # Create user
        await conn.execute(
            """
            INSERT INTO users (id, email, password_hash, role)
            VALUES ($1, $2, $3, 'client')
            ON CONFLICT (email) DO NOTHING
            """,
            user_id, "test@tokoabc.com", hashed_password
        )
        
        # Create client
        await conn.execute(
            """
            INSERT INTO clients (id, name, plan, status)
            VALUES ($1, $2, $3, 'active')
            ON CONFLICT (id) DO NOTHING
            """,
            client_id, "Toko ABC (Test)", "pro"
        )
        
        # Link user to client
        await conn.execute(
            """
            INSERT INTO user_clients (user_id, client_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            user_id, client_id
        )
        
        # Create API key (always create new one)
        await conn.execute(
            """
            DELETE FROM api_keys WHERE client_id = $1
            """,
            client_id
        )
        
        await conn.execute(
            """
            INSERT INTO api_keys (client_id, key_hash, is_active, rate_limit_per_minute)
            VALUES ($1, $2, true, 10)
            """,
            client_id, api_key
        )
        
        print("✅ User registered/updated successfully!")
        print(f"   Email: test@tokoabc.com")
        print(f"   Password: test123")
        print(f"   Client ID: {client_id}")
        print(f"   API Key: {api_key}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(quick_register())
