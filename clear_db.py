"""
Clear all data from test database
WARNING: This will delete ALL data from the database!
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "acm_ai"),
    "user": os.getenv("DATABASE_USER", "acm_ai"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
}


async def clear_database():
    """Delete all data from database tables"""
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        print("⚠️  WARNING: This will delete ALL data from the database!")
        print("Database:", DB_CONFIG["database"])
        
        response = input("\nType 'YES' to confirm deletion: ")
        
        if response != "YES":
            print("❌ Cancelled. No data was deleted.")
            return

        print("\n🗑️  Deleting data...")

        # Delete in reverse order of foreign key dependencies
        await conn.execute("DELETE FROM document_chunks")
        print("  ✅ Deleted document_chunks")

        await conn.execute("DELETE FROM documents")
        print("  ✅ Deleted documents")

        await conn.execute("DELETE FROM chat_messages")
        print("  ✅ Deleted chat_messages")

        await conn.execute("DELETE FROM chat_sessions")
        print("  ✅ Deleted chat_sessions")

        await conn.execute("DELETE FROM usage_logs")
        print("  ✅ Deleted usage_logs")

        await conn.execute("DELETE FROM user_clients")
        print("  ✅ Deleted user_clients")

        await conn.execute("DELETE FROM users")
        print("  ✅ Deleted users")

        await conn.execute("DELETE FROM api_keys")
        print("  ✅ Deleted api_keys")

        await conn.execute("DELETE FROM clients")
        print("  ✅ Deleted clients")

        print("\n🎉 Database cleared successfully!")
        print("You can now run: python seed_db.py")

    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(clear_database())
