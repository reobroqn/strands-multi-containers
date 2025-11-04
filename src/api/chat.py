import json
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel

from src.agent.agent_core import AgentOrchestrator
from src.config import settings
from src.services.redis_client import RedisClient

router = APIRouter()


# Dependency to check Redis availability
async def verify_redis():
    """Dependency to ensure Redis is available"""
    if not await RedisClient.ping():
        logger.error("Redis unavailable")
        raise HTTPException(status_code=503, detail="Redis service unavailable")


# Models
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    chat_id: str
    message_count: int
    status: str  # "new", "active", or other states


@router.post("/chat/{chat_id}")
async def start_chat(
    chat_id: str,
    request: ChatRequest,
    _: Annotated[None, Depends(verify_redis)],
):
    """Start a chat with streaming SSE response"""
    logger.info(f"chat_id=<{chat_id}> | Starting chat with message: {request.message[:100]}")

    try:
        orchestrator = AgentOrchestrator(chat_id)

        async def generate_sse():
            """Generate Server-Sent Events stream"""
            try:
                async for chunk in orchestrator.stream_response(request.message):
                    yield f"data: {chunk}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"chat_id=<{chat_id}> | Stream error: {e}")
                yield f"data: [ERROR] {e!s}\n\n"

        return StreamingResponse(
            generate_sse(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        logger.error(f"chat_id=<{chat_id}> | Failed to start chat: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/chats")
async def list_chats():
    """List all chat sessions"""
    try:
        session_dir = Path(settings.session_dir)

        if not session_dir.exists():
            return {"chats": [], "count": 0}

        chats = []
        for session_file in session_dir.glob("*.json"):
            try:
                with open(session_file) as f:
                    data = json.load(f)

                chats.append(
                    {
                        "chat_id": data.get("agent_id", session_file.stem),
                        "status": "active",
                        "message_count": len(data.get("messages", [])),
                        "updated_at": data.get("updated_at"),
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to read session {session_file.name}: {e}")
                continue

        logger.info(f"Listed {len(chats)} chats")
        return {"chats": chats, "count": len(chats)}

    except Exception as e:
        logger.error(f"Failed to list chats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/chat/{chat_id}", response_model=ChatResponse)
async def get_chat(chat_id: str):
    """Get chat session details"""
    try:
        session_dir = Path(settings.session_dir)
        session_file = session_dir / f"{chat_id}.json"

        if not session_file.exists():
            # Return new chat info instead of 404 for better UX
            return ChatResponse(
                chat_id=chat_id,
                message_count=0,
                status="new",
            )

        with open(session_file) as f:
            data = json.load(f)

        return ChatResponse(
            chat_id=chat_id,
            message_count=len(data.get("messages", [])),
            status="active",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"chat_id=<{chat_id}> | Failed to get chat: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/chat/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat session"""
    try:
        session_dir = Path(settings.session_dir)
        session_file = session_dir / f"{chat_id}.json"

        if session_file.exists():
            session_file.unlink()
            logger.info(f"chat_id=<{chat_id}> | Deleted chat session")
            return {"status": "deleted", "chat_id": chat_id}
        else:
            raise HTTPException(status_code=404, detail="Chat not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"chat_id=<{chat_id}> | Failed to delete chat: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
