"""
Seed database with initial test data
Run this script after creating the database schema
"""

import asyncio
import asyncpg
import uuid
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "acm_ai"),
    "user": os.getenv("DATABASE_USER", "acm_ai"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
}


async def seed_database():
    """Seed database with test data"""
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        print("🌱 Seeding database...")

        # 1. Create test client
        client_id = uuid.uuid4()
        
        # Use 'pro' plan which is valid in the database constraints
        # Valid values: 'free', 'basic', 'pro' (from clients_plan_check constraint)
        await conn.execute(
            """
            INSERT INTO clients (id, name, plan, status)
            VALUES ($1, $2, 'pro', 'active')
        """,
            client_id,
            "Toko ABC (Test)",
        )
        
        print(f"✅ Created client: {client_id} - Plan: pro")

        # 2. Create API key for testing
        api_key = "client-key-1"  # Same as before for compatibility
        await conn.execute(
            """
            INSERT INTO api_keys (client_id, key_hash, is_active, rate_limit_per_minute)
            VALUES ($1, $2, $3, $4)
        """,
            client_id,
            api_key,
            True,
            10,
        )
        print(f"✅ Created API key: {api_key}")

        # 3. Create test user (admin)
        admin_id = uuid.uuid4()
        # In production, hash password properly!
        await conn.execute(
            """
            INSERT INTO users (id, email, password_hash, role)
            VALUES ($1, $2, $3, $4)
        """,
            admin_id,
            "admin@tokoabc.com",
            "$2b$12$dummy.hash.for.testing.purposes.only",  # TODO: proper hash
            "admin",
        )
        print(f"✅ Created admin user: admin@tokoabc.com")

        # 4. Link user to client
        await conn.execute(
            """
            INSERT INTO user_clients (user_id, client_id)
            VALUES ($1, $2)
        """,
            admin_id,
            client_id,
        )
        print(f"✅ Linked admin to client")

        # 5. Create sample document
        doc_id = uuid.uuid4()
        await conn.execute(
            """
            INSERT INTO documents (id, client_id, title, source)
            VALUES ($1, $2, $3, $4)
        """,
            doc_id,
            client_id,
            "FAQ Toko ABC",
            "manual_upload",
        )
        print(f"✅ Created sample document: {doc_id}")

        # 6. Create sample document chunks
        sample_chunks = [
            "Toko ABC buka setiap hari pukul 08:00 - 20:00",
            "Kami menjual berbagai produk elektronik dan gadget",
            "Gratis ongkir untuk pembelian di atas Rp 500.000",
        ]

        for idx, content in enumerate(sample_chunks):
            chunk_id = uuid.uuid4()
            await conn.execute(
                """
                INSERT INTO document_chunks (id, document_id, chunk_index, content)
                VALUES ($1, $2, $3, $4)
            """,
                chunk_id,
                doc_id,
                idx,
                content,
            )
        print(f"✅ Created {len(sample_chunks)} document chunks")

        print("\n🎉 Database seeded successfully!")
        print("\nTest credentials:")
        print(f"  Client ID: {client_id}")
        print(f"  API Key: {api_key}")
        print(f"  Admin Email: admin@tokoabc.com")
        print(f"\n💡 TIP: If you run this again, delete existing data first or it will error.")

    except asyncpg.exceptions.UniqueViolationError as e:
        print(f"⚠️  Data already exists: {e}")
        print("To re-seed, delete the existing data first.")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
