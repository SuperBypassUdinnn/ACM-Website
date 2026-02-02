"""
Check database constraints for debugging
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


async def check_constraints():
    """Check table constraints"""
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        print("🔍 Checking database constraints...\n")

        # Check clients table constraints
        print("=== CLIENTS TABLE ===")
        constraints = await conn.fetch(
            """
            SELECT conname, pg_get_constraintdef(oid) as definition
            FROM pg_constraint
            WHERE conrelid = 'clients'::regclass
        """
        )

        for c in constraints:
            print(f"{c['conname']}: {c['definition']}")

        print("\n=== CLIENTS TABLE STRUCTURE ===")
        columns = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'clients'
            ORDER BY ordinal_position
        """
        )

        for col in columns:
            print(
                f"  {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})"
            )

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_constraints())
