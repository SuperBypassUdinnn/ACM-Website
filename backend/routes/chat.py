"""
Chat Routes

Handles chat endpoint and template message retrieval.
"""

from fastapi import APIRouter, Header
import uuid as uuid_lib
from backend.models import ChatReq
from backend.dependencies import verify_api_key, check_rate_limit
from backend.services.chat import retrieve_context, call_ollama
from backend.services.session import (
    get_or_create_session,
    get_chat_history,
    save_message,
    get_client_prompt,
    get_template_message
)
from backend.services.usage import log_usage

router = APIRouter()


@router.post("/chat")
async def chat(req: ChatReq, x_api_key: str = Header(...)):
    """
    Main chat endpoint with RAG and database integration
    """
    # 1. Verify API key and get client info
    client_info = await verify_api_key(x_api_key)
    client_id = client_info["client_id"]

    # 2. Check rate limit
    await check_rate_limit(x_api_key, client_info["rate_limit"])

    # 3. Get or create session
    session_id = await get_or_create_session(req.session_id, client_id)

    # 4. Get chat history from database
    history = await get_chat_history(session_id, limit=5)

    # 5. Retrieve context from vector DB (client-specific)
    context = retrieve_context(req.message, client_id=str(client_id))

    # 6. Format memory block from database history
    memory_block = ""
    for h in history:
        if h["role"] == "user":
            memory_block += f"User: {h['content']}\n"
        elif h["role"] == "assistant":
            memory_block += f"Assistant: {h['content']}\n\n"

    # 7. Load client-specific system prompt
    client_prompt = await get_client_prompt(client_id)

    # 8. Build prompt with client-specific system prompt
    full_prompt = f"""
{client_prompt}

Conversation so far:
{memory_block}

Context:
{context}

User question:
{req.message}

Answer:
"""

    # 9. Generate response
    reply = call_ollama(full_prompt).strip()

    # 10. Estimate token counts (rough estimate)
    tokens_in = len(full_prompt.split())
    tokens_out = len(reply.split())

    # 11. Save messages to database
    await save_message(session_id, "user", req.message, tokens_in)
    await save_message(session_id, "assistant", reply, tokens_out)

    # 12. Log usage
    await log_usage(client_id, x_api_key, "/chat", tokens_in, tokens_out)

    return {"reply": reply}


@router.get("/template_message")
async def get_template(x_api_key: str = Header(...)):
    """
    Get client's initial chat template message
    """
    # Verify API key and get client info
    client_info = await verify_api_key(x_api_key)
    client_id = client_info["client_id"]
    
    # Get template message
    template = await get_template_message(client_id)
    
    # Return template or default message
    return {"template": template}
