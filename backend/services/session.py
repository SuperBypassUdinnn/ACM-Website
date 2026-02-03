"""
Session Management Service

Handles chat session creation and management.
"""

import uuid as uuid_lib
from backend.database import get_db_pool
from backend.config import DEFAULT_SYSTEM_PROMPT


async def get_or_create_session(
    session_identifier: str, client_id: uuid_lib.UUID
) -> uuid_lib.UUID:
    """Get existing session or create new one"""
    db_pool = get_db_pool()
    
    async with db_pool.acquire() as conn:
        # Try to get existing session
        session = await conn.fetchrow(
            """
            SELECT id FROM chat_sessions
            WHERE user_identifier = $1 AND client_id = $2
        """,
            session_identifier,
            client_id,
        )

        if session:
            return session["id"]

        # Create new session
        new_session = await conn.fetchrow(
            """
            INSERT INTO chat_sessions (client_id, user_identifier)
            VALUES ($1, $2)
            RETURNING id
        """,
            client_id,
            session_identifier,
        )

        return new_session["id"]


async def get_chat_history(session_id: uuid_lib.UUID, limit: int = 5) -> list:
    """Get recent chat history for session"""
    db_pool = get_db_pool()
    
    async with db_pool.acquire() as conn:
        messages = await conn.fetch(
            """
            SELECT role, content
            FROM chat_messages
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """,
            session_id,
            limit,
        )

        # Return in chronological order (oldest first)
        return list(reversed(messages))


async def save_message(
    session_id: uuid_lib.UUID, role: str, content: str, token_count: int = 0
):
    """Save message to database"""
    db_pool = get_db_pool()
    
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO chat_messages (session_id, role, content, token_count, created_at)
            VALUES ($1, $2, $3, $4, NOW())
        """,
            session_id,
            role,
            content,
            token_count,
        )


async def get_client_prompt(client_id: uuid_lib.UUID) -> str:
    """
    Load client-specific system prompt from database.
    Returns client's custom prompt if set, otherwise returns DEFAULT_SYSTEM_PROMPT.
    """
    db_pool = get_db_pool()
    
    async with db_pool.acquire() as conn:
        result = await conn.fetchval(
            "SELECT system_prompt FROM clients WHERE id = $1",
            client_id
        )
        return result if result else DEFAULT_SYSTEM_PROMPT


async def get_template_message(client_id: uuid_lib.UUID) -> str:
    """Get client's template message"""
    db_pool = get_db_pool()
    
    async with db_pool.acquire() as conn:
        template = await conn.fetchval(
            "SELECT template_message FROM clients WHERE id = $1",
            client_id
        )
        return template if template else "Halo! Ada yang bisa saya bantu?"
