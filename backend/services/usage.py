"""
Usage Logging Service

Handles API usage tracking and analytics.
"""

import uuid as uuid_lib
from backend.database import get_db_pool


async def log_usage(
    client_id: uuid_lib.UUID,
    api_key: str,
    endpoint: str,
    tokens_in: int,
    tokens_out: int,
):
    """Log API usage for analytics"""
    db_pool = get_db_pool()
    
    async with db_pool.acquire() as conn:
        # Get api_key ID from key_hash
        api_key_row = await conn.fetchrow(
            "SELECT id FROM api_keys WHERE key_hash = $1", api_key
        )

        if api_key_row:
            await conn.execute(
                """
                INSERT INTO usage_logs (client_id, api_key_id, endpoint, tokens_in, tokens_out)
                VALUES ($1, $2, $3, $4, $5)
            """,
                client_id,
                api_key_row["id"],  # Use api_keys.id, not client_id
                endpoint,
                tokens_in,
                tokens_out,
            )
