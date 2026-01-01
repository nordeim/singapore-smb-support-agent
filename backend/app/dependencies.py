"""FastAPI dependency injection functions for Singapore SMB Support Agent."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.memory.manager import MemoryManager

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_memory_manager(
    db: AsyncSession = Depends(get_db),
) -> MemoryManager:
    """Dependency for getting MemoryManager instance."""
    return MemoryManager(db)


class BusinessContext:
    """Business context for Singapore SMB operations."""

    def __init__(
        self,
        timezone_str: str = settings.TIMEZONE,
        business_hours_start: str = settings.BUSINESS_HOURS_START,
        business_hours_end: str = settings.BUSINESS_HOURS_END,
    ):
        self.timezone = timezone_str
        self.business_hours_start = business_hours_start
        self.business_hours_end = business_hours_end

    def get_current_time(self) -> datetime:
        """Get current time in Singapore timezone."""
        return datetime.now(UTC).astimezone()

    def is_business_hours(self) -> bool:
        """Check if current time is within business hours."""
        now = self.get_current_time()
        current_hour = now.hour
        current_minute = now.minute
        current_time_minutes = current_hour * 60 + current_minute

        start_hour, start_minute = map(int, self.business_hours_start.split(":"))
        end_hour, end_minute = map(int, self.business_hours_end.split(":"))
        start_minutes = start_hour * 60 + start_minute
        end_minutes = end_hour * 60 + end_minute

        return start_minutes <= current_time_minutes < end_minutes

    def get_business_hours_display(self) -> str:
        """Get formatted business hours string."""
        return (
            f"{self.business_hours_start} - {self.business_hours_end} ({self.timezone})"
        )


def get_business_context() -> BusinessContext:
    """Dependency for getting business context."""
    return BusinessContext()


async def get_current_user_mvp(
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """MVP user dependency using session ID instead of JWT token."""
    from sqlalchemy import text


    result = await db.execute(
        text("""SELECT u.id, u.email, u.is_active, u.data_retention_days
               FROM users u
               JOIN conversations c ON u.id = c.user_id
               WHERE c.session_id = :session_id AND u.is_active = TRUE"""),
        {"session_id": session_id},
    )
    user = result.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    return {
        "id": user[0],
        "email": user[1],
        "is_active": user[2],
        "data_retention_days": user[3],
    }


async def get_session_data(
    session_id: str,
    memory_manager: MemoryManager = Depends(get_memory_manager),
) -> dict:
    """Dependency for getting session data from Redis."""
    session_data = await memory_manager.get_session(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired",
        )

    return session_data
