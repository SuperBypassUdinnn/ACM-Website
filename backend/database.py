"""
Database Module

Handles database connection pooling and lifecycle management.
"""

import asyncpg
from contextlib import asynccontextmanager
from backend.config import DB_CONFIG

# Global database pool
db_pool = None


@asynccontextmanager
async def lifespan(app):
    """
    Lifecycle manager for database connection pool.
    Called on app startup and shutdown.
    """
    global db_pool
    
    # Startup
    print("🔌 Connecting to database...")
    db_pool = await asyncpg.create_pool(**DB_CONFIG, min_size=2, max_size=10)
    print("✅ Database pool created")
    
    yield
    
    # Shutdown
    print("🔌 Closing database pool...")
    await db_pool.close()
    print("✅ Database pool closed")


def get_db_pool():
    """Get the global database pool instance."""
    return db_pool
