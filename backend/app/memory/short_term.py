"""Redis configuration and session management."""

from typing import Optional
import redis.asyncio as redis
from app.config import settings


class RedisManager:
    """Redis connection manager."""

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        """Get or create Redis client instance."""
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """Close Redis connection."""
        if cls._instance is not None:
            await cls._instance.close()
            cls._instance = None


redis_client = RedisManager.get_client()


class ShortTermMemory:
    """Short-term memory using Redis for session storage."""

    SESSION_PREFIX = "session:"
    SESSION_TTL = settings.PDPA_SESSION_TTL_MINUTES * 60

    @staticmethod
    async def get_session(session_id: str) -> Optional[dict]:
        """Retrieve session data from Redis."""
        key = f"{ShortTermMemory.SESSION_PREFIX}{session_id}"
        return await redis_client.get(key)

    @staticmethod
    async def save_session(session_id: str, data: dict) -> None:
        """Save session data to Redis with TTL."""
        import json

        key = f"{ShortTermMemory.SESSION_PREFIX}{session_id}"
        value = json.dumps(data)
        await redis_client.setex(key, ShortTermMemory.SESSION_TTL, value)

    @staticmethod
    async def add_message(session_id: str, message: dict) -> None:
        """Add message to session in Redis."""
        import json

        session_data = await ShortTermMemory.get_session(session_id)
        if session_data is None:
            session_data = {"messages": []}

        session_data["messages"].append(message)
        await ShortTermMemory.save_session(session_id, session_data)

    @staticmethod
    async def delete_session(session_id: str) -> None:
        """Delete session from Redis."""
        key = f"{ShortTermMemory.SESSION_PREFIX}{session_id}"
        await redis_client.delete(key)

    @staticmethod
    async def increment_message_count(session_id: str) -> int:
        """Increment message count for session."""
        key = f"{ShortTermMemory.SESSION_PREFIX}{session_id}:count"
        return await redis_client.incr(key)
