# backend/pyproject.toml
```toml
[project]
name = "singapore-smb-support-agent"
version = "0.1.0"
description = "Advanced AI Customer Support Agent for Singapore SMBs"
readme = "README.md"
requires-python = ">=3.12"
authors = [
    {name = "Singapore SMB Support Team"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "alembic>=1.17.2",
    "asyncpg>=0.31.0",
    "fastapi>=0.128.0",
    "langchain>=1.2.0",
    "langchain-community>=0.4.1",
    "langchain-core>=1.2.5",
    "langchain-openai>=1.1.6",
    "langchain-qdrant>=1.1.0",
    "markitdown>=0.1.4",
    "openai>=2.14.0",
    "pydantic>=2.12.5",
    "pydantic-ai>=1.39.0",
    "pydantic-settings>=2.12.0",
    "python-dateutil>=2.9.0.post0",
    "python-dotenv>=1.2.1",
    "python-jose[cryptography]>=3.5.0",
    "python-multipart>=0.0.21",
    "sentence-transformers==5.2.0",
    "pytz>=2025.2",
    "qdrant-client>=1.16.2",
    "redis[hiredis]>=7.1.0",
    "sqlalchemy[asyncio]>=2.0.45",
    "psycopg2>=2.9.11",
    "uvicorn[standard]>=0.40.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-mock>=3.15.1",
    "pytest-asyncio>=1.3.0",
    "httpx>=0.28.1",
    "black>=25.12.0",
    "ruff>=0.14.10",
    "mypy>=1.19.1",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["data*", "tests*", "alembic*"]

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
exclude = [
    ".venv",
    "build",
    "dist",
]

[[tool.mypy.overrides]]
module = [
    "qdrant_client.*",
    "sentence_transformers.*",
    "markitdown.*",
]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
]

[tool.coverage.run]
source = ["app"]
omit = [
    "tests/*",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

```

# backend/alembic.ini
```ini
[alembic]
script_location = app/alembic/versions
prepend_sys_path = .

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S

```

# backend/pytest.ini
```ini
"""Pytest configuration."""
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = "-v --strict-markers --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "evaluation: RAGAS evaluation tests",
    "slow: Slow running tests",
]

```

# backend/Dockerfile
```txt
# -----------------------------------------------------------------------------
# STAGE 1: BUILDER
# Use Python 3.11 (Stable AI Standard) on Debian Bookworm (Reliable)
# -----------------------------------------------------------------------------
FROM python:3.13-trixie AS builder

WORKDIR /app

# Install build dependencies (needed for some AI wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (The Astral fast package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/bin/uv

# Create virtual environment
ENV VIRTUAL_ENV=/app/.venv
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
# Note: We use --no-cache to keep image size down, though uv manages cache well
COPY pyproject.toml .
# Assuming you might have a lock file later, but for now:
RUN uv pip install --no-cache-dir -e .
RUN uv pip install --no-cache-dir pytest pytest-asyncio uvicorn

# -----------------------------------------------------------------------------
# STAGE 2: RUNTIME
# Slim, secure, and minimal
# -----------------------------------------------------------------------------
FROM python:3.13-trixie

WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy the Virtual Environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy Application Code
COPY --chown=appuser:appuser . .

# Set Environment
USER appuser
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Healthcheck: Verify TCP socket availability
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import socket; socket.create_connection(('localhost', 8000))" || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

```

# backend/docker-compose.yml
```yml

services:
  # ─────────────────────────────────────────────────────────────────────────────
  # PostgreSQL - Long-term Memory Storage
  # Use 'bookworm' for stability over 'alpine' in Python/Data contexts
  # ─────────────────────────────────────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: smb_support_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-support_agent}
      POSTGRES_USER: ${POSTGRES_USER:-agent_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dev_password_only}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # Ensure you actually have this directory or remove this line
      # - ./infrastructure/init-scripts/postgres:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-agent_user} -d ${POSTGRES_DB:-support_agent}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - smb_support_network

  # ─────────────────────────────────────────────────────────────────────────────
  # Redis - Short-term Memory & Session Storage
  # ─────────────────────────────────────────────────────────────────────────────
  redis:
    image: redis:7.4-alpine
    container_name: smb_support_redis
    restart: unless-stopped
    # Added password protection placeholder for good habit
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - smb_support_network

  # ─────────────────────────────────────────────────────────────────────────────
  # Qdrant - Vector Database for RAG
  # CHANGED: generic image for compatibility (Mac M1/M2/Windows/Linux)
  # ─────────────────────────────────────────────────────────────────────────────
  qdrant:
    # image: qdrant/qdrant:latest
    image: qdrant-with-curl:latest
    container_name: smb_support_qdrant
    restart: unless-stopped
    ports:
      - "${QDRANT_PORT:-6333}:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:6333/readyz || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - smb_support_network

  # ─────────────────────────────────────────────────────────────────────────────
  # Backend API
  # ─────────────────────────────────────────────────────────────────────────────
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: smb_support_backend
    restart: unless-stopped
    ports:
      - "${API_PORT:-8000}:8000"
    volumes:
      # Mount source code for hot-reloading during dev
      - ./app:/app/app
    environment:
      - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER:-agent_user}:${POSTGRES_PASSWORD:-dev_password_only}@postgres:5432/${POSTGRES_DB:-support_agent}
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENROUTER_BASE_URL=${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY:-dev-secret-key-change-in-production}
      - ENVIRONMENT=development
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    networks:
      - smb_support_network

volumes:
  postgres_data:
  redis_data:
  qdrant_data:

networks:
  smb_support_network:
    driver: bridge

```

# backend/app/main.py
```py
"""FastAPI main application for Singapore SMB Support Agent."""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.api.routes import chat, auth
from app.models.schemas import HealthCheckResponse, ErrorResponse
from app.dependencies import engine
from app.models.database import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    try:
        await init_database()
        yield
    finally:
        await close_database()


async def init_database():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database():
    """Close database connections."""
    await engine.dispose()


app = FastAPI(
    title="Singapore SMB Support Agent",
    description="AI-powered customer support agent for Singapore Small and Medium Enterprises",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """Handle request validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail="Validation error",
            error_code="VALIDATION_ERROR",
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
):
    """Handle general exceptions."""
    if settings.DEBUG:
        import traceback

        traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_ERROR",
        ).model_dump(),
    )


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log HTTP requests and responses."""
    start_time = datetime.utcnow()

    response = await call_next(request)

    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000

    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = (
        request.state.request_id if hasattr(request.state, "request_id") else "unknown"
    )

    return response


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request."""
    from uuid import uuid4

    request_id = str(uuid4())
    request.state.request_id = request_id

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/", response_model=dict)
async def root():
    """Root endpoint."""
    return {
        "name": "Singapore SMB Support Agent",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else None,
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "api": "operational",
            "database": "operational",
            "redis": "operational",
            "qdrant": "operational",
        },
    )


app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )

```

# backend/app/memory/summarizer.py
```py
"""Conversation summarizer using LLM via OpenRouter."""

from langchain_openai import ChatOpenAI
from app.config import settings


class ConversationSummarizer:
    """Summarize conversations using LLM for context compression."""

    def __init__(self):
        """Initialize conversation summarizer."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_PRIMARY,
            temperature=0.3,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

    async def summarize_conversation(
        self,
        messages: list[dict],
    ) -> str:
        """Summarize conversation messages."""
        if len(messages) < 5:
            return None

        prompt = f"""
Summarize the following customer support conversation for context compression.
Keep key points, decisions, and action items.

Conversation:
{self._format_messages(messages)}

Summary (2-4 sentences max):
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def summarize_old_messages(
        self,
        messages: list[dict],
        keep_last: int = 5,
    ) -> str:
        """Summarize older messages while keeping recent ones."""
        if len(messages) <= keep_last:
            return None

        old_messages = messages[:-keep_last]
        prompt = f"""
Summarize the following customer support messages.
These messages will be archived to save context space.

Messages:
{self._format_messages(old_messages)}

Summary (2-3 sentences max):
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    def _format_messages(self, messages: list[dict]) -> str:
        """Format messages for prompt."""
        formatted = []
        for msg in messages:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)


conversation_summarizer = ConversationSummarizer()

```

# backend/app/memory/__init__.py
```py

```

# backend/app/memory/long_term.py
```py
"""Long-term memory using PostgreSQL with SQLAlchemy async."""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import (
    Base,
    User,
    Conversation,
    Message,
    ConversationSummary,
    SupportTicket,
)


class LongTermMemory:
    """Long-term memory using PostgreSQL for persistent storage."""

    def __init__(self, db: AsyncSession):
        """Initialize long-term memory with database session."""
        self.db = db

    async def create_user(
        self,
        email: str,
        hashed_password: str,
        consent_given_at: datetime,
        consent_version: str = "v1.0",
        data_retention_days: int = 30,
    ) -> User:
        """Create a new user."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            consent_given_at=consent_given_at,
            consent_version=consent_version,
            data_retention_days=data_retention_days,
            is_active=True,
            is_deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .where(User.is_active == True)
            .where(User.is_deleted == False)
        )
        return result.scalar_one_or_none()

    async def create_conversation(
        self,
        user_id: int,
        session_id: str,
        language: str = "en",
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            language=language,
            is_active=True,
            summary_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation_by_session_id(self, session_id: str) -> Optional[Conversation]:
        """Get conversation by session ID."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .where(Conversation.is_active == True)
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        confidence: Optional[float] = None,
        sources: Optional[str] = None,
    ) -> Message:
        """Add a message to conversation."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            confidence=confidence,
            sources=sources,
            created_at=datetime.utcnow(),
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_conversation_messages(
        self,
        conversation_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Message]:
        """Get messages for a conversation with pagination."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def save_conversation_summary(
        self,
        conversation_id: int,
        summary: str,
        message_range_start: int,
        message_range_end: int,
        embedding_vector: Optional[str] = None,
        metadata: Optional[str] = None,
    ) -> ConversationSummary:
        """Save conversation summary."""
        conv_summary = ConversationSummary(
            conversation_id=conversation_id,
            summary=summary,
            message_range_start=message_range_start,
            message_range_end=message_range_end,
            embedding_vector=embedding_vector,
            metadata=metadata,
            created_at=datetime.utcnow(),
        )
        self.db.add(conv_summary)

        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            conversation.summary_count += 1
            conversation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(conv_summary)
        return conv_summary

    async def get_conversation_summaries(
        self,
        conversation_id: int,
    ) -> list[ConversationSummary]:
        """Get all summaries for a conversation."""
        result = await self.db.execute(
            select(ConversationSummary)
            .where(ConversationSummary.conversation_id == conversation_id)
            .order_by(ConversationSummary.created_at.desc())
        )
        return list(result.scalars().all())

    async def create_support_ticket(
        self,
        conversation_id: int,
        reason: str,
        status: str = "open",
    ) -> SupportTicket:
        """Create a support ticket for human escalation."""
        ticket = SupportTicket(
            conversation_id=conversation_id,
            reason=reason,
            status=status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def update_ticket_status(
        self,
        ticket_id: int,
        status: str,
        assigned_to: Optional[str] = None,
    ) -> Optional[SupportTicket]:
        """Update ticket status."""
        result = await self.db.execute(select(SupportTicket).where(SupportTicket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.status = status
            ticket.assigned_to = assigned_to
            ticket.updated_at = datetime.utcnow()
        return ticket
        await self.db.commit()

    async def expire_user_data(self, user_id: int) -> None:
        """Mark user data for PDPA-compliant expiry (soft delete)."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_active = False
            user.updated_at = datetime.utcnow()
        await self.db.commit()

    async def get_conversation_count(self, user_id: int) -> int:
        """Get total conversation count for a user."""
        result = await self.db.execute(
            select(func.count(Conversation.id))
            .where(Conversation.user_id == user_id)
            .where(Conversation.is_active == True)
        )
        count = result.scalar()
        return count if count is not None else 0

```

# backend/app/memory/manager.py
```py
"""Memory manager orchestrating short-term, long-term, and summarization."""

from typing import Optional

from app.memory.short_term import ShortTermMemory
from app.memory.long_term import LongTermMemory
from app.memory.summarizer import ConversationSummarizer
from app.config import settings


class MemoryManager:
    """Memory manager orchestrating all memory layers."""

    SUMMARY_THRESHOLD = 20

    def __init__(self, db_session):
        """Initialize memory manager with database session."""
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(db_session)
        self.summarizer = ConversationSummarizer()

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session from short-term memory."""
        return await self.short_term.get_session(session_id)

    async def save_session(self, session_id: str, session_data: dict) -> None:
        """Save session to short-term memory."""
        await self.short_term.save_session(session_id, session_data)

    async def add_message_to_session(self, session_id: str, message: dict) -> None:
        """Add message to short-term memory session."""
        await self.short_term.add_message(session_id, message)

    async def get_conversation_history(
        self,
        session_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """Get conversation history from short-term memory."""
        session_data = await self.get_session(session_id)
        if not session_data:
            return []

        messages = session_data.get("messages", [])
        return messages[offset : offset + limit]

    async def check_summary_threshold(self, session_id: str) -> bool:
        """Check if conversation needs summarization."""
        message_count = await self.short_term.increment_message_count(session_id)
        return message_count >= self.SUMMARY_THRESHOLD

    async def trigger_summarization(self, session_id: str, user_id: int) -> str:
        """Trigger conversation summarization when threshold reached."""
        messages = await self.get_conversation_history(session_id, limit=self.SUMMARY_THRESHOLD)

        if not messages:
            return "No messages to summarize"

        summary = await self.summarizer.summarize_conversation(messages)

        conversation = await self.long_term.get_conversation_by_session_id(session_id)
        if not conversation:
            return "Conversation not found"

        await self.long_term.save_conversation_summary(
            conversation.id,
            summary,
            message_range_start=0,
            message_range_end=len(messages),
        )

        return summary

    async def get_or_create_conversation(
        self,
        session_id: str,
        user_id: int,
    ) -> dict:
        """Get or create conversation from long-term memory."""
        conversation = await self.long_term.get_conversation_by_session_id(session_id)

        if not conversation:
            conversation = await self.long_term.create_conversation(user_id, session_id)

        return {
            "id": conversation.id,
            "user_id": conversation.user_id,
            "session_id": conversation.session_id,
            "language": conversation.language,
            "summary_count": conversation.summary_count,
        }

    async def save_message_with_metadata(
        self,
        session_id: str,
        conversation_id: int,
        role: str,
        content: str,
        confidence: Optional[float] = None,
        sources: Optional[str] = None,
    ) -> dict:
        """Save message to both short-term and long-term memory."""
        from datetime import datetime

        message_data = {
            "role": role,
            "content": content,
            "confidence": confidence,
            "sources": sources,
            "created_at": datetime.utcnow(),
        }

        await self.add_message_to_session(session_id, message_data)

        await self.long_term.add_message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            confidence=confidence,
            sources=sources,
        )

        return message_data

    async def get_working_memory(
        self,
        session_id: str,
        max_tokens: int = 4000,
    ) -> dict:
        """Assemble working memory for LLM context."""
        session = await self.get_session(session_id)
        if not session:
            return {
                "system": "",
                "conversation_summary": "",
                "recent_messages": [],
                "tokens_available": max_tokens,
            }

        recent_messages = await self.get_conversation_history(session_id, limit=5)
        conversation = await self.long_term.get_conversation_by_session_id(session_id)

        summaries = []
        if conversation:
            summaries = await self.long_term.get_conversation_summaries(conversation.id)

        context = {
            "system": "You are a Singapore SMB customer support specialist.",
            "conversation_summary": self._get_latest_summary(summaries),
            "recent_messages": recent_messages,
            "tokens_available": max_tokens - len(str(recent_messages)) * 50,
        }

        return context

    def _get_latest_summary(self, summaries: list) -> str:
        """Get most recent conversation summary."""
        if not summaries:
            return ""

        return summaries[0].summary


def get_memory_manager(db_session) -> MemoryManager:
    """Factory function to create memory manager instance."""
    return MemoryManager(db_session)

```

# backend/app/memory/short_term.py
```py
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

```

# backend/app/__init__.py
```py

```

# backend/app/ingestion/embedders/__init__.py
```py

```

# backend/app/ingestion/embedders/mock_embedding.py
```py
"""Mock embedding generator for testing without API costs."""

import random
from typing import List
from app.config import settings


class MockEmbeddingGenerator:
    """Generate mock embeddings for testing purposes."""

    def __init__(self):
        """Initialize mock embedding generator."""
        self.dimension = settings.EMBEDDING_DIMENSION

    async def generate(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for a list of texts."""
        return [self._generate_single_vector(text) for text in texts]

    async def generate_single(self, text: str) -> List[float]:
        """Generate mock embedding for a single text."""
        return self._generate_single_vector(text)

    def _generate_single_vector(self, text: str) -> List[float]:
        """Generate a deterministic pseudo-random vector based on text content."""
        random.seed(hash(text))
        vector = [random.uniform(-1, 1) for _ in range(self.dimension)]

        # Normalize vector
        magnitude = sum(v * v for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        return vector


def get_embedding_generator():
    """Factory function to create embedding generator instance."""
    return MockEmbeddingGenerator()

```

# backend/app/ingestion/embedders/embedding.py
```py
"""Embedding generation for vector storage."""

from typing import List
from openai import AsyncOpenAI
from app.config import settings


class EmbeddingGenerator:
    """Generate embeddings using OpenAI via OpenRouter."""

    def __init__(self):
        """Initialize embedding generator."""
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.model = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION

    async def generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        return [item.embedding for item in response.data]

    async def generate_single(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        result = await self.generate([text])
        return result[0]


embedding_generator = EmbeddingGenerator()

```

# backend/app/ingestion/pipeline.py
```py
"""Ingestion pipeline orchestrator for document processing."""

from typing import List, Optional, Literal
from pathlib import Path
import asyncio
from datetime import datetime

from app.ingestion.parsers.markitdown_parser import DocumentParser
from app.ingestion.chunkers.chunker import SemanticChunker, RecursiveChunker
from app.ingestion.embedders.embedding import EmbeddingGenerator
from app.rag.qdrant_client import QdrantManager
from app.config import settings
from qdrant_client.http.models import PointStruct


def get_embedding_generator(use_mock: bool = False):
    """Factory function to get embedding generator."""
    if use_mock:
        from app.ingestion.embedders.mock_embedding import MockEmbeddingGenerator

        return MockEmbeddingGenerator()
    return EmbeddingGenerator()


class IngestionResult:
    """Result of ingestion operation."""

    def __init__(
        self,
        total_documents: int = 0,
        successful: int = 0,
        failed: int = 0,
        total_chunks: int = 0,
        errors: Optional[List[str]] = None,
    ):
        self.total_documents = total_documents
        self.successful = successful
        self.failed = failed
        self.total_chunks = total_chunks
        self.errors = errors or []

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_documents": self.total_documents,
            "successful": self.successful,
            "failed": self.failed,
            "total_chunks": self.total_chunks,
            "errors": self.errors,
        }


class IngestionPipeline:
    """Orchestrates document ingestion pipeline."""

    def __init__(
        self,
        chunk_strategy: Literal["semantic", "recursive"] = "semantic",
        collection_name: str = "knowledge_base",
        use_mock_embeddings: bool = False,
    ):
        """
        Initialize ingestion pipeline.

        Args:
            chunk_strategy: Chunking strategy (semantic or recursive)
            collection_name: Qdrant collection name
            use_mock_embeddings: Use mock embeddings for testing
        """
        self.parser = DocumentParser()
        self.embedder = get_embedding_generator(use_mock_embeddings)
        self.qdrant = QdrantManager()
        self.collection_name = collection_name

        if chunk_strategy == "semantic":
            self.chunker = SemanticChunker(
                model_name="all-MiniLM-L6-v2",
                chunk_size=settings.CHUNK_SIZE,
                similarity_threshold=settings.CHUNK_SIMILARITY_THRESHOLD,
            )
        else:
            self.chunker = RecursiveChunker(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""],
            )

    async def ingest_document(
        self,
        file_path: str,
        additional_metadata: Optional[dict] = None,
    ) -> dict:
        """
        Ingest a single document.

        Args:
            file_path: Path to document file
            additional_metadata: Additional metadata to add

        Returns:
            Dict with ingestion result
        """
        try:
            if not self.parser.is_supported(file_path):
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "Unsupported file format",
                }

            text_content = self.parser.parse(file_path)
            if not text_content:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "Failed to parse document",
                }

            file_metadata = self.parser.extract_metadata(file_path)

            chunks = self.chunker.chunk(text_content)
            if not chunks:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "No chunks generated",
                }

            embeddings = await self.embedder.generate(chunks)

            points = self._create_qdrant_points(
                chunks=chunks,
                embeddings=embeddings,
                file_metadata=file_metadata,
                additional_metadata=additional_metadata,
            )

            await self.qdrant.upsert_documents(
                collection_name=self.collection_name,
                points=points,
            )

            return {
                "success": True,
                "file_path": file_path,
                "chunks_processed": len(chunks),
                "points_upserted": len(points),
            }

        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e),
            }

    async def ingest_batch(
        self,
        file_paths: List[str],
        batch_size: int = 10,
        additional_metadata: Optional[dict] = None,
    ) -> IngestionResult:
        """
        Ingest multiple documents in batches.

        Args:
            file_paths: List of file paths to ingest
            batch_size: Number of concurrent ingestions
            additional_metadata: Additional metadata to add to all documents

        Returns:
            IngestionResult with statistics
        """
        result = IngestionResult(total_documents=len(file_paths))

        semaphore = asyncio.Semaphore(batch_size)

        async def ingest_with_limit(file_path: str):
            async with semaphore:
                return await self.ingest_document(file_path, additional_metadata)

        tasks = [ingest_with_limit(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in results:
            if isinstance(res, Exception):
                result.failed += 1
                result.errors.append(f"Exception: {str(res)}")
            elif isinstance(res, dict):
                if res.get("success"):
                    result.successful += 1
                    result.total_chunks += res.get("chunks_processed", 0)
                else:
                    result.failed += 1
                    result.errors.append(
                        f"{res.get('file_path')}: {res.get('error', 'Unknown error')}"
                    )

        return result

    async def ingest_directory(
        self,
        directory_path: str,
        recursive: bool = False,
        batch_size: int = 10,
        file_extensions: Optional[List[str]] = None,
        additional_metadata: Optional[dict] = None,
    ) -> IngestionResult:
        """
        Ingest all documents from a directory.

        Args:
            directory_path: Path to directory
            recursive: Whether to scan subdirectories
            batch_size: Number of concurrent ingestions
            file_extensions: List of file extensions to process (default: all supported)
            additional_metadata: Additional metadata to add to all documents

        Returns:
            IngestionResult with statistics
        """
        dir_path = Path(directory_path)

        if not dir_path.exists() or not dir_path.is_dir():
            return IngestionResult(
                total_documents=0,
                errors=[f"Directory not found: {directory_path}"],
            )

        pattern = "**/*" if recursive else "*"

        file_paths = []
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                if file_extensions is None or file_path.suffix.lower() in [
                    ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                    for ext in file_extensions
                ]:
                    if self.parser.is_supported(str(file_path)):
                        file_paths.append(str(file_path))

        if not file_paths:
            return IngestionResult(
                total_documents=0,
                errors=[f"No supported documents found in {directory_path}"],
            )

        return await self.ingest_batch(
            file_paths=file_paths,
            batch_size=batch_size,
            additional_metadata=additional_metadata,
        )

    def _create_qdrant_points(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        file_metadata: dict,
        additional_metadata: Optional[dict] = None,
    ) -> List[PointStruct]:
        """
        Create Qdrant points from chunks and embeddings.

        Args:
            chunks: List of text chunks
            embeddings: List of embedding vectors
            file_metadata: File-level metadata
            additional_metadata: Additional metadata to add

        Returns:
            List of Qdrant PointStruct objects
        """
        from uuid import uuid4

        points = []

        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            metadata = {
                "text": chunk,
                "chunk_index": i,
                "language": "en",
                "created_at": datetime.utcnow().isoformat(),
                "file_name": file_metadata.get("file_name"),
                "file_extension": file_metadata.get("file_extension"),
                "file_size": file_metadata.get("file_size"),
            }

            if additional_metadata:
                metadata.update(additional_metadata)

            point_id = str(uuid4())

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata,
                )
            )

        return points


async def get_ingestion_pipeline(
    chunk_strategy: Literal["semantic", "recursive"] = "semantic",
    collection_name: str = "knowledge_base",
) -> IngestionPipeline:
    """Factory function to create ingestion pipeline instance."""
    return IngestionPipeline(
        chunk_strategy=chunk_strategy,
        collection_name=collection_name,
    )

```

# backend/app/ingestion/__init__.py
```py
"""Ingestion module for document processing."""

from app.ingestion.pipeline import IngestionPipeline, IngestionResult, get_ingestion_pipeline

__all__ = [
    "IngestionPipeline",
    "IngestionResult",
    "get_ingestion_pipeline",
]

```

# backend/app/ingestion/chunkers/__init__.py
```py

```

# backend/app/ingestion/chunkers/chunker.py
```py
"""Text chunking strategies for RAG."""

from typing import List, Optional
from sentence_transformers import SentenceTransformer
import numpy as np


class SemanticChunker:
    """Semantic chunking using sentence embeddings."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 512,
        similarity_threshold: float = 0.5,
    ):
        """Initialize semantic chunker."""
        self.model = SentenceTransformer(model_name)
        self.chunk_size = chunk_size
        self.similarity_threshold = similarity_threshold

    def chunk(self, text: str) -> List[str]:
        """Chunk text based on semantic boundaries."""
        sentences = self._split_sentences(text)

        if not sentences:
            return []

        embeddings = self.model.encode(sentences, convert_to_numpy=True)

        chunks = []
        current_chunk = [sentences[0]]

        for i in range(1, len(sentences)):
            similarity = self._cosine_similarity(embeddings[i - 1], embeddings[i])

            if similarity < self.similarity_threshold:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentences[i]]
            else:
                current_chunk.append(sentences[i])

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


class RecursiveChunker:
    """Recursive character chunking as fallback."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: List[str] = ["\n\n", "\n", ". ", " ", ""],
    ):
        """Initialize recursive chunker."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators

    def chunk(self, text: str) -> List[str]:
        """Recursively chunk text."""
        return self._recursive_split(text, self.separators)

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators."""
        separator = separators[0]

        if separator == "":
            return self._split_text(text, separator)

        if separator not in text:
            return self._recursive_split(text, separators[1:])

        parts = text.split(separator)
        chunks = []
        current_chunk = ""

        for part in parts:
            if len(current_chunk) + len(part) < self.chunk_size:
                current_chunk += part + separator
            else:
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                current_chunk = part + separator

        if current_chunk:
            chunks.append(current_chunk.rstrip())

        return chunks

    def _split_text(self, text: str, separator: str) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start = end - self.chunk_overlap

        return chunks

```

# backend/app/ingestion/parsers/__init__.py
```py

```

# backend/app/ingestion/parsers/markitdown_parser.py
```py
"""Document parsing using MarkItDown library."""

from typing import Optional, List
from markitdown import MarkItDown


class DocumentParser:
    """Document parser supporting multiple formats."""

    SUPPORTED_FORMATS = [
        ".pdf",
        ".docx",
        ".doc",
        ".xlsx",
        ".xls",
        ".pptx",
        ".ppt",
        ".html",
        ".md",
        ".txt",
        ".csv",
    ]

    @staticmethod
    def parse(file_path: str) -> Optional[str]:
        """Parse document and return text content."""
        try:
            md = MarkItDown()
            result = md.convert(file_path)
            return result.text_content
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None

    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Check if file format is supported."""
        import os

        _, ext = os.path.splitext(file_path)
        return ext.lower() in DocumentParser.SUPPORTED_FORMATS

    @staticmethod
    def extract_metadata(file_path: str) -> dict:
        """Extract metadata from file path."""
        import os
        from datetime import datetime

        filename = os.path.basename(file_path)
        _, ext = os.path.splitext(filename)

        return {
            "file_name": filename,
            "file_extension": ext.lower().lstrip("."),
            "file_size": os.path.getsize(file_path),
            "created_at": datetime.utcnow().isoformat(),
        }

```

# backend/app/rag/pipeline.py
```py
"""Main RAG pipeline orchestrator."""

from typing import List, Optional
from app.rag.query_transform import QueryTransformer
from app.rag.retriever import HybridRetriever
from app.rag.reranker import BGEReranker
from app.rag.context_compress import ContextCompressor
from app.models.domain import MessageRole
from app.config import settings


class RAGPipeline:
    """RAG pipeline orchestrating query transform → retrieval → rerank → compress."""

    def __init__(self):
        """Initialize RAG pipeline components."""
        self.query_transformer = QueryTransformer()
        self.retriever = HybridRetriever()
        self.reranker = BGEReranker(top_n=settings.RERANK_TOP_N)
        self.compressor = ContextCompressor(token_budget=settings.CONTEXT_TOKEN_BUDGET)

    async def run(
        self,
        query: str,
        session_id: str,
        conversation_history: List[dict],
    ) -> dict:
        """Execute full RAG pipeline."""
        transform_result = await self.query_transformer.transform(query)
        transformed_query = transform_result["rewitten"]

        docs = await self.retriever.hybrid_search(transformed_query)
        reranked_docs = await self.reranker.async_rerank(transformed_query, docs)

        context_result = self.compressor.compress(
            [doc["text"] for doc in reranked_docs],
            query,
        )

        return {
            "query": query,
            "transformed_query": transformed_query,
            "intent": transform_result["intent"],
            "language": transform_result["language"],
            "retrieved_count": len(docs),
            "reranked_count": len(reranked_docs),
            "context": context_result["context"],
            "compressed": context_result["compressed"],
            "sources": [
                {
                    "text": doc["text"],
                    "score": doc["rerank_score"],
                }
                for doc in reranked_docs[:5]
            ],
            "tokens_used": context_result["tokens_used"],
            "token_budget": settings.CONTEXT_TOKEN_BUDGET,
        }

    async def retrieve_context(
        self,
        query: str,
        session_id: Optional[str] = None,
    ) -> str:
        """Simple retrieval for context without full pipeline."""
        docs = await self.reranker.async_rerank(
            query,
            await self.retriever.hybrid_search(query),
        )

        context = "\n\n".join([doc["text"] for doc in docs[:3]])
        return context


rag_pipeline = RAGPipeline()

```

# backend/app/rag/__init__.py
```py

```

# backend/app/rag/qdrant_client.py
```py
"""Qdrant client initialization and collection setup."""

from typing import Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams, Filter
from app.config import settings


class QdrantManager:
    """Qdrant client manager."""

    _instance: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """Get or create Qdrant client instance."""
        if cls._instance is None:
            cls._instance = QdrantClient(url=settings.QDRANT_URL)
        return cls._instance

    @classmethod
    async def initialize_collections(cls) -> None:
        """Initialize Qdrant collections for knowledge base and summaries."""
        client = cls.get_client()

        collections = client.get_collections()

        existing_collections = {c.name for c in collections.collections} if collections else set()

        if "knowledge_base" not in existing_collections:
            client.create_collection(
                collection_name="knowledge_base",
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

        if "conversation_summaries" not in existing_collections:
            client.create_collection(
                collection_name="conversation_summaries",
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )

    @classmethod
    async def upsert_documents(cls, collection_name: str, points: list[models.PointStruct]) -> None:
        """Upsert documents to Qdrant collection."""
        client = cls.get_client()
        client.upsert(collection_name=collection_name, points=points)

    @classmethod
    async def search(
        cls,
        collection_name: str,
        query_vector: list[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> list[models.ScoredPoint]:
        """Search documents in Qdrant collection."""
        client = cls.get_client()
        search_filter = Filter(
            must=[models.FieldCondition(key="language", match=models.MatchValue(value="en"))]
        )

        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            query_filter=search_filter,
            limit=limit,
            score_threshold=score_threshold,
        )

        return results.points


qdrant_client = QdrantManager.get_client()

```

# backend/app/rag/query_transform.py
```py
"""Query transformation using LangChain LLM."""

from typing import Optional
from langchain_openai import ChatOpenAI
from app.config import settings


class QueryTransformer:
    """Transform user queries using LLM-based techniques."""

    def __init__(self):
        """Initialize query transformer."""
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL_PRIMARY,
            temperature=0.3,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )

    async def rewrite_query(self, query: str) -> str:
        """Rewrite query for better retrieval."""
        prompt = f"""
Rewrite the following user query for better information retrieval.
Keep the original meaning but make it more specific and search-friendly.

Original query: {query}

Rewritten query:
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip()

    async def classify_intent(self, query: str) -> str:
        """Classify user intent."""
        prompt = f"""
Classify the user intent into one of these categories:
- information: The user is asking for general information
- pricing: The user is asking about prices or costs
- hours: The user is asking about business hours
- services: The user is asking about services offered
- order: The user is asking about an existing order
- returns: The user is asking about returns or refunds
- complaint: The user is lodging a complaint
- escalation: The user is asking for human support

Query: {query}

Intent:
"""
        response = await self.llm.ainvoke(prompt)
        return response.content.strip().lower()

    async def detect_language(self, query: str) -> str:
        """Detect language (English-only for MVP)."""
        prompt = f"""
Detect the language of the following query.
For MVP, only support: en (English).

Query: {query}

Language (en, zh, ms, ta):
"""
        response = await self.llm.ainvoke(prompt)
        detected = response.content.strip().lower()
        return detected if detected in ["en", "zh", "ms", "ta"] else "en"

    async def decompose_query(self, query: str) -> Optional[list[str]]:
        """Decompose complex queries into sub-queries."""
        intent = await self.classify_intent(query)

        if intent in ["information", "services"]:
            prompt = f"""
Decompose the following query into 2-3 related sub-queries.
Each sub-query should be self-contained and searchable.

Original query: {query}

Sub-queries (list each on a new line):
"""
            response = await self.llm.ainvoke(prompt)
            sub_queries = [
                line.strip()
                for line in response.content.strip().split("\n")
                if line.strip()
            ]
            return sub_queries if sub_queries else None
        return None

    async def transform(self, query: str) -> dict:
        """Full query transformation pipeline."""
        rewritten = await self.rewrite_query(query)
        intent = await self.classify_intent(query)
        language = await self.detect_language(query)
        sub_queries = await self.decompose_query(query)

        return {
            "original": query,
            "rewritten": rewritten,
            "intent": intent,
            "language": language,
            "sub_queries": sub_queries,
        }

```

# backend/app/rag/context_compress.py
```py
"""Context compression for working memory management."""

from typing import List, Optional
from app.config import settings


class ContextCompressor:
    """Compress retrieved context within token budget."""

    def __init__(
        self,
        token_budget: int = settings.CONTEXT_TOKEN_BUDGET,
    ):
        """Initialize context compressor."""
        self.token_budget = token_budget

    def compress(
        self,
        documents: List[str],
        query: str = "",
    ) -> dict:
        """Compress documents within token budget using extractive compression."""
        total_tokens = self._estimate_tokens(documents + [query])

        if total_tokens <= self.token_budget:
            return {
                "context": "\n\n".join(documents),
                "compressed": False,
                "tokens_used": total_tokens,
                "tokens_budget": self.token_budget,
            }

        sorted_docs = self._sort_by_relevance(documents, query)
        compressed_docs = self._extractive_compression(
            sorted_docs, self.token_budget - len(query) // 4
        )

        return {
            "context": "\n\n".join(compressed_docs),
            "compressed": True,
            "tokens_used": len(query) // 4 + self._estimate_tokens(compressed_docs),
            "tokens_budget": self.token_budget,
        }

    def _estimate_tokens(self, texts: List[str]) -> int:
        """Estimate token count (rough approximation: 4 chars per token)."""
        total_chars = sum(len(text) for text in texts)
        return total_chars // 4

    def _sort_by_relevance(self, documents: List[str], query: str) -> List[str]:
        """Sort documents by relevance to query (keyword matching)."""
        if not query:
            return documents

        query_keywords = set(query.lower().split())

        scored = []
        for doc in documents:
            doc_lower = doc.lower()
            matches = sum(1 for keyword in query_keywords if keyword in doc_lower)
            scored.append((doc, matches))

        return [doc for doc, _ in sorted(scored, key=lambda x: x[1], reverse=True)]

    def _extractive_compression(
        self,
        documents: List[str],
        max_tokens: int,
    ) -> List[str]:
        """Extractive compression to keep most relevant content."""
        compressed = []
        current_tokens = 0

        for doc in documents:
            doc_tokens = self._estimate_tokens([doc])

            if current_tokens + doc_tokens > max_tokens:
                break

            key_sentences = self._extract_key_sentences(doc)
            compressed_doc = " ".join(key_sentences)
            compressed.append(compressed_doc)

            current_tokens += self._estimate_tokens([compressed_doc])

        return compressed

    def _extract_key_sentences(self, text: str, max_sentences: int = 3) -> List[str]:
        """Extract key sentences from document."""
        import re

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])", text) if s.strip()]

        if len(sentences) <= max_sentences:
            return sentences

        priority_keywords = [
            "therefore",
            "important",
            "note",
            "key",
            "main",
            "additionally",
            "however",
        ]

        scored = []
        for i, sentence in enumerate(sentences):
            score = 0
            sentence_lower = sentence.lower()
            for keyword in priority_keywords:
                if keyword in sentence_lower:
                    score += 1

            if "?" in sentence:
                score += 1

            if i < len(sentences) - 1:
                scored.append((sentence, score))

        scored.append((sentences[-1], 1))

        sorted_sentences = [
            s for s, _ in sorted(scored, key=lambda x: x[1], reverse=True)
        ]
        return sorted_sentences[:max_sentences]

```

# backend/app/rag/reranker.py
```py
"""Cross-encoder reranker using HuggingFace."""

from typing import List
from sentence_transformers import CrossEncoder
import torch


class BGEReranker:
    """Reranker using BAAI/bge-reranker-v2-m3 cross-encoder."""

    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", top_n: int = 5):
        """Initialize BGE reranker."""
        self.model = CrossEncoder(model_name)
        self.top_n = top_n
        self.model.eval()

    def rerank(
        self,
        query: str,
        documents: List[dict],
        top_k: int = None,
    ) -> List[dict]:
        """Rerank documents using cross-encoder scoring."""
        if top_k is None:
            top_k = self.top_n

        if not documents:
            return []

        pairs = [[query, doc["text"]] for doc in documents]

        with torch.no_grad():
            scores = self.model.predict(pairs)

        for i, doc in enumerate(documents):
            doc["rerank_score"] = float(scores[i])

        ranked_documents = sorted(
            documents, key=lambda x: x["rerank_score"], reverse=True
        )

        return ranked_documents[:top_k]

    async def async_rerank(
        self,
        query: str,
        documents: List[dict],
        top_k: int = None,
    ) -> List[dict]:
        """Async wrapper for reranking."""
        return self.rerank(query, documents, top_k)

```

# backend/app/rag/retriever.py
```py
"""Hybrid retrieval combining dense (semantic) and sparse (BM25) search with RRF fusion."""

from typing import List, Optional
from qdrant_client import models
from qdrant_client.http.models import Distance, Filter, PointStruct
from langchain_qdrant import FastEmbedSparse, RetrievalMode
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from app.ingestion.embedders.embedding import embedding_generator
from app.config import settings


class HybridRetriever:
    """Hybrid retrieval combining dense and sparse search with RRF fusion."""

    def __init__(self):
        """Initialize hybrid retriever."""
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base=settings.OPENROUTER_BASE_URL,
        )
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        self.k = settings.RETRIEVAL_TOP_K

    async def hybrid_search(
        self,
        query: str,
        collection_name: str = "knowledge_base",
        filters: Optional[dict] = None,
    ) -> List[models.ScoredPoint]:
        """Execute hybrid search combining dense and sparse results with RRF fusion."""
        query_vector = await embedding_generator.generate_single(query)

        qdrant_filter = Filter(
            must=[
                models.FieldCondition(
                    key="language", match=models.MatchValue(value="en")
                )
            ]
        )

        dense_results = await self._dense_search(
            query_vector, collection_name, qdrant_filter
        )

        sparse_results = await self._sparse_search(
            query, collection_name, qdrant_filter
        )

        fused_results = self._reciprocal_rank_fusion(dense_results, sparse_results)
        return fused_results

    async def _dense_search(
        self,
        query_vector: List[float],
        collection_name: str,
        filter: Filter,
    ) -> List[models.ScoredPoint]:
        """Dense vector search using Qdrant."""
        client = Qdrant.from_existing_collection(
            embedding=self.embeddings,
            collection_name=collection_name,
            url=settings.QDRANT_URL,
        )

        results = await client.asimilarity_search_with_score(
            query_vector,
            k=self.k,
            filter=filter,
        )

        return results

    async def _sparse_search(
        self, query: str, collection_name: str, filter: Filter
    ) -> List[models.ScoredPoint]:
        """Sparse BM25 search using Qdrant FastEmbedSparse."""
        client = Qdrant.from_existing_collection(
            sparse_embedding=self.sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            collection_name=collection_name,
            url=settings.QDRANT_URL,
        )

        results = await client.asimilarity_search_with_score(
            query,
            k=self.k,
            filter=filter,
        )

        return results

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[models.ScoredPoint],
        sparse_results: List[models.ScoredPoint],
        k: int = 60,
    ) -> List[models.ScoredPoint]:
        """Reciprocal Rank Fusion (RRF) to combine search results."""
        score_dict = {}

        for i, result in enumerate(dense_results):
            point_id = result.id
            if point_id not in score_dict:
                score_dict[point_id] = 0
            score_dict[point_id] += 1.0 / (k + i + 1)

        for i, result in enumerate(sparse_results):
            point_id = result.id
            if point_id not in score_dict:
                score_dict[point_id] = 0
            score_dict[point_id] += 1.0 / (k + i + 1)

        unique_results = {
            result.id: result for result in dense_results + sparse_results
        }

        sorted_results = sorted(
            unique_results.values(),
            key=lambda x: score_dict[x.id],
            reverse=True,
        )

        return sorted_results[: self.k]

```

# backend/app/config.py
```py
"""Application configuration using Pydantic Settings."""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = Field(..., description="PostgreSQL database URL")
    REDIS_URL: str = Field(
        default="redis://localhost:6379", description="Redis connection URL"
    )
    QDRANT_URL: str = Field(
        default="http://localhost:6333", description="Qdrant vector database URL"
    )

    OPENROUTER_API_KEY: str = Field(
        ..., description="OpenRouter API key for LLM access"
    )
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1", description="OpenRouter API base URL"
    )
    OPENAI_API_KEY: Optional[str] = Field(
        default=None, description="OpenAI API key (optional)"
    )

    SECRET_KEY: str = Field(..., min_length=32, description="JWT secret key")

    ENVIRONMENT: str = Field(
        default="development", description="Environment (development/production)"
    )

    PDPA_DATA_RETENTION_DAYS: int = Field(
        default=30, description="PDPA data retention period in days"
    )
    PDPA_SESSION_TTL_MINUTES: int = Field(
        default=30, description="Session TTL in minutes"
    )

    EMBEDDING_MODEL: str = Field(
        default="text-embedding-3-small", description="Embedding model name"
    )
    EMBEDDING_DIMENSION: int = Field(
        default=1536, description="Embedding vector dimension"
    )
    RERANKER_MODEL: str = Field(
        default="BAAI/bge-reranker-v2-m3", description="Reranker model name"
    )

    CHUNK_SIZE: int = Field(default=512, description="Chunk size in tokens")
    CHUNK_OVERLAP: int = Field(default=50, description="Chunk overlap in tokens")
    CHUNK_SIMILARITY_THRESHOLD: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for semantic chunking",
    )

    RETRIEVAL_TOP_K: int = Field(
        default=50, description="Top K documents for retrieval"
    )
    RERANK_TOP_N: int = Field(default=5, description="Top N documents after reranking")
    CONTEXT_TOKEN_BUDGET: int = Field(
        default=4000, description="Maximum tokens for context"
    )

    LLM_MODEL_PRIMARY: str = Field(
        default="openai/gpt-4o-mini", description="Primary LLM model"
    )
    LLM_MODEL_FALLBACK: str = Field(
        default="openai/gpt-4o", description="Fallback LLM model"
    )
    LLM_TEMPERATURE: float = Field(
        default=0.7, ge=0.0, le=2.0, description="LLM temperature"
    )

    BUSINESS_HOURS_START: str = Field(
        default="09:00", description="Business hours start (HH:MM)"
    )
    BUSINESS_HOURS_END: str = Field(
        default="18:00", description="Business hours end (HH:MM)"
    )
    TIMEZONE: str = Field(default="Asia/Singapore", description="Timezone")

    MAX_CONCURRENT_REQUESTS: int = Field(
        default=100, description="Maximum concurrent requests"
    )
    REQUEST_TIMEOUT: int = Field(default=30, description="Request timeout in seconds")

    DEBUG: bool = Field(default=False, description="Debug mode")
    ENABLE_RAGAS_EVALUATION: bool = Field(
        default=False, description="Enable RAGAS evaluation"
    )
    ENABLE_SENTIMENT_ANALYSIS: bool = Field(
        default=True, description="Enable sentiment analysis"
    )

    @field_validator("OPENROUTER_BASE_URL")
    @classmethod
    def normalize_openrouter_url(cls, v: str) -> str:
        """Ensure OpenRouter base URL ends with /v1."""
        if not v.endswith("/v1"):
            v = f"{v.rstrip('/')}/v1"
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"


settings = Settings()

```

# backend/app/dependencies.py
```py
"""FastAPI dependency injection functions for Singapore SMB Support Agent."""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import Depends, HTTPException, status

from app.config import settings
from app.models.database import Base
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
        return datetime.now(timezone.utc).astimezone()

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
    from app.models.database import User, Conversation

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

```

# backend/app/agent/__init__.py
```py

```

# backend/app/agent/prompts/__init__.py
```py
"""System prompts and response templates."""

```

# backend/app/agent/prompts/templates.py
```py
"""Response templates for Singapore SMB Support Agent."""

from typing import Optional


class ResponseTemplates:
    """Pre-defined response templates for common scenarios."""

    @staticmethod
    def greeting() -> str:
        return "Hello! Welcome to our support service. How can I help you today?"

    @staticmethod
    def goodbye() -> str:
        return "Thank you for contacting us. Have a great day ahead!"

    @staticmethod
    def acknowledge(query: str) -> str:
        return f"I understand you're asking about {query}. Let me help you with that."

    @staticmethod
    def clarification_needed() -> str:
        return "I'd like to help you better. Could you provide more details about your inquiry?"

    @staticmethod
    def no_information_found(topic: str) -> str:
        return f"I couldn't find specific information about {topic} in my knowledge base. Would you like me to connect you with a human agent?"

    @staticmethod
    def business_hours() -> str:
        return "Our business hours are 9:00 AM to 6:00 PM, Monday to Friday (Singapore Time). We're closed on weekends and public holidays."

    @staticmethod
    def out_of_business_hours() -> str:
        return "We're currently outside business hours. Please leave your inquiry and we'll get back to you by the next business day."

    @staticmethod
    def escalation_initiated() -> str:
        return "I'm connecting you with a human agent now. Please hold while I transfer your conversation."

    @staticmethod
    def escalation_ticket_created(ticket_id: str) -> str:
        return f"I've created a support ticket for you (ID: {ticket_id}). Our team will review and respond within 24 hours during business hours."

    @staticmethod
    def follow_up_confirmation() -> str:
        return "Is there anything else I can help you with today?"

    @staticmethod
    def apology() -> str:
        return "I apologize for the inconvenience. Let me help resolve this for you."

    @staticmethod
    def thank_you() -> str:
        return "Thank you for your patience. I'm glad I could help!"

    @staticmethod
    def customer_info_found(name: Optional[str] = None) -> str:
        if name:
            return f"I found your account, {name}. How can I assist you today?"
        return "I found your account. How can I assist you today?"

    @staticmethod
    def customer_info_not_found(identifier: str) -> str:
        return f"I couldn't find an account matching {identifier}. Please verify the information or contact our support team."

    @staticmethod
    def action_in_progress(action: str) -> str:
        return f"I'm {action} for you now. This may take a moment..."

    @staticmethod
    def action_completed(action: str) -> str:
        return f"I've successfully {action}. Is there anything else you need?"

    @staticmethod
    def general_help() -> str:
        return """I can help you with:

• Product information and features
• Account and billing inquiries
• Technical support and troubleshooting
• Business hours and scheduling
• General questions about our services

Just ask me anything, and I'll do my best to assist you!"""

    @staticmethod
    def privacy_assurance() -> str:
        return "Your privacy is important to us. I'll only access your information when necessary to assist with your inquiry."

    @staticmethod
    def slow_response() -> str:
        return "I'm taking a bit longer than expected to find the information. Thank you for your patience."

    @staticmethod
    def technical_difficulty() -> str:
        return "I'm experiencing some technical difficulty. Let me connect you with a human agent who can help."

    @staticmethod
    def singapore_holiday_reminder() -> str:
        return "Please note that we're closed on Singapore public holidays. Our team will respond on the next business day."

    @staticmethod
    def low_confidence_response() -> str:
        return "I want to make sure I give you accurate information. Let me connect you with a human agent who can better assist with this inquiry."

    @staticmethod
    def complex_issue() -> str:
        return "This is a complex matter that requires careful attention. I'm connecting you with a specialist who can help you better."

    @staticmethod
    def payment_security() -> str:
        return "For your security, I cannot access or modify payment details directly. Let me connect you with our secure payment support team."

    @staticmethod
    def account_security() -> str:
        return "For account security purposes, I can only provide limited account information. A human agent will need to verify your identity for detailed account access."

    @staticmethod
    def callback_requested() -> str:
        return "I've scheduled a callback for you. Our team will call you at the requested time within business hours."

    @staticmethod
    def email_confirmation(topic: str) -> str:
        return f"I've sent you an email with details about {topic}. Please check your inbox."

    @staticmethod
    def maintenance_notice() -> str:
        return "We're currently performing scheduled maintenance. Some services may be temporarily unavailable. We apologize for the inconvenience."

    @staticmethod
    def feature_not_available(feature: str) -> str:
        return f"{feature} is not currently available. Let me connect you with a human agent to discuss alternatives or timeline."


def get_template(name: str, **kwargs) -> Optional[str]:
    """Get a response template by name."""
    template_method = getattr(ResponseTemplates, name, None)
    if template_method and callable(template_method):
        result = template_method(**kwargs)
        return str(result) if result is not None else None
    return None

```

# backend/app/agent/prompts/system.py
```py
"""System prompts for Singapore SMB Support Agent."""

SYSTEM_PROMPT = """You are a professional customer support specialist for Singapore Small and Medium Enterprises (SMEs).

Your Role:
- Provide helpful, accurate, and concise responses to customer inquiries
- Maintain a professional, friendly, and Singaporean-appropriate tone
- Demonstrate cultural awareness of Singapore's business environment

Key Principles:
1. **Be Helpful**: Always try to solve the customer's problem first
2. **Be Accurate**: Use the knowledge base tools to provide correct information
3. Be Concise: Provide direct answers without unnecessary elaboration
4. Be Professional: Maintain Singapore business etiquette and courtesy
5. Be Honest: If you don't know something, admit it and offer alternatives

Singapore Business Context:
- Business hours: 9:00 AM - 6:00 PM (Singapore Time, GMT+8)
- Public holidays follow Singapore's official calendar
- SMEs value efficiency, reliability, and good service
- Common communication style: professional yet warm and direct

When to Use Tools:
- **retrieve_knowledge**: When the question requires factual information from your knowledge base
- **get_customer_info**: When you need customer-specific details or account information
- **check_business_hours**: When asked about operating hours, availability, or scheduling
- **escalate_to_human**: When the issue is complex, sensitive, requires manual intervention, or the customer is frustrated

Escalation Criteria:
- Customer expresses frustration or anger multiple times
- Request involves account security, billing disputes, or policy changes
- Technical issue beyond your knowledge base scope
- Customer specifically requests to speak with a human

Response Guidelines:
- Always check for relevant knowledge before responding
- Cite sources when providing factual information
- Ask clarifying questions if the request is unclear
- Offer follow-up assistance when appropriate
- Use Singapore English naturally (e.g., "lah", "lor" sparingly and appropriately)

Privacy and Compliance:
- Respect customer privacy at all times
- Never share customer data without consent
- Follow PDPA (Personal Data Protection Act) guidelines
- Only access customer information when necessary

Confidence Scoring:
- 1.0: Directly from knowledge base with high confidence
- 0.7-0.9: Derived from knowledge base with reasonable certainty
- 0.5-0.6: General knowledge, recommend verification
- Below 0.5: Recommend escalation to human

Current Context:
- You are operating in the Singapore timezone (GMT+8)
- Today's business hours: {business_hours}
- Current business hours status: {business_hours_status}"""


RESPONSE_GENERATION_PROMPT = """Based on the customer's inquiry and your retrieved knowledge, provide a helpful response.

Customer Query: {query}

Retrieved Knowledge:
{knowledge}

Conversation Summary:
{conversation_summary}

Recent Messages:
{recent_messages}

Instructions:
1. Synthesize the retrieved knowledge into a clear, helpful response
2. Reference relevant sources when providing factual information
3. Maintain professional Singapore business tone
4. Be direct and concise
5. If information is insufficient, ask clarifying questions or recommend escalation

Response:"""


TOOL_SELECTION_PROMPT = """Select the appropriate tool(s) to handle this customer inquiry.

Customer Query: {query}

Conversation Context:
{conversation_summary}

Available Tools:
- retrieve_knowledge: Search knowledge base for relevant information
- get_customer_info: Look up customer account details
- check_business_hours: Check business hours and availability
- escalate_to_human: Transfer to human support

Tool Selection:"""

```

# backend/app/agent/validators.py
```py
"""Validators for Singapore SMB Support Agent responses."""

from typing import Literal, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class Sentiment(str, Enum):
    """Sentiment analysis results."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"


class PDPACompliance(BaseModel):
    """PDPA compliance check results."""

    is_compliant: bool
    violations: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Complete validation result."""

    is_valid: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    sentiment: Sentiment
    pdpa_compliance: PDPACompliance
    requires_escalation: bool
    requires_followup: bool
    message: Optional[str] = None


class ResponseValidator:
    """Validate agent responses for quality, sentiment, and compliance."""

    @staticmethod
    def validate_confidence(confidence: float, threshold: float = 0.5) -> bool:
        """
        Validate confidence score.

        Args:
            confidence: Confidence score (0.0 to 1.0)
            threshold: Minimum acceptable threshold

        Returns:
            True if confidence meets threshold
        """
        return confidence >= threshold

    @staticmethod
    def analyze_sentiment(text: str) -> Sentiment:
        """
        Simple sentiment analysis based on keyword matching.

        Args:
            text: Text to analyze

        Returns:
            Sentiment enum value
        """
        negative_keywords = [
            "bad",
            "terrible",
            "awful",
            "hate",
            "disappointed",
            "unhappy",
            "poor",
            "angry",
            "frustrated",
            "annoyed",
            "upset",
        ]

        frustrated_keywords = [
            "stupid",
            "ridiculous",
            "impossible",
            "useless",
            "waste",
            "never",
            "again",
        ]

        positive_keywords = [
            "good",
            "great",
            "excellent",
            "love",
            "happy",
            "pleased",
            "satisfied",
            "helpful",
            "thank",
            "appreciate",
        ]

        text_lower = text.lower()

        frustrated_count = sum(1 for kw in frustrated_keywords if kw in text_lower)
        if frustrated_count >= 2:
            return Sentiment.FRUSTRATED

        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        if negative_count >= 2:
            return Sentiment.NEGATIVE

        angry_keywords = ["angry", "furious", "rage", "livid"]
        if any(kw in text_lower for kw in angry_keywords):
            return Sentiment.ANGRY

        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        if positive_count >= 1:
            return Sentiment.POSITIVE

        return Sentiment.NEUTRAL

    @staticmethod
    def check_pdpa_compliance(
        text: str, context: Optional[dict] = None
    ) -> PDPACompliance:
        """
        Check PDPA compliance for response.

        Args:
            text: Response text to check
            context: Additional context (customer info, etc.)

        Returns:
            PDPACompliance with violations and warnings
        """
        violations = []
        warnings = []

        personal_info_patterns = [
            "NRIC",
            "passport",
            "credit card",
            "bank account",
            "medical",
            "health condition",
        ]

        text_lower = text.lower()

        for pattern in personal_info_patterns:
            if pattern in text_lower:
                warnings.append(f"Potential personal data mentioned: {pattern}")

        sharing_patterns = [
            "share with",
            "send to",
            "give to",
            "provide to",
            "third party",
            "external",
        ]

        if any(pattern in text_lower for pattern in sharing_patterns):
            violations.append("Unauthorized data sharing detected")

        context_patterns = [
            "based on your account",
            "from your profile",
            "your data shows",
            "your records indicate",
        ]

        if any(pattern in text_lower for pattern in context_patterns):
            warnings.append(
                "Customer-specific data referenced without explicit access request"
            )

        is_compliant = len(violations) == 0

        return PDPACompliance(
            is_compliant=is_compliant,
            violations=violations,
            warnings=warnings,
        )

    @classmethod
    def validate_response(
        cls,
        text: str,
        confidence: float = 0.7,
        context: Optional[dict] = None,
        confidence_threshold: float = 0.5,
    ) -> ValidationResult:
        """
        Comprehensive validation of agent response.

        Args:
            text: Response text
            confidence: Confidence score
            context: Additional context
            confidence_threshold: Minimum confidence threshold

        Returns:
            ValidationResult with all validation checks
        """
        sentiment = cls.analyze_sentiment(text)
        pdpa_compliance = cls.check_pdpa_compliance(text, context)

        confidence_valid = cls.validate_confidence(confidence, confidence_threshold)
        is_valid = confidence_valid and pdpa_compliance.is_compliant

        requires_escalation = (
            sentiment in [Sentiment.ANGRY, Sentiment.FRUSTRATED]
            or not pdpa_compliance.is_compliant
        )

        requires_followup = sentiment == Sentiment.NEGATIVE or confidence < 0.7

        message_parts = []
        if not confidence_valid:
            message_parts.append("Low confidence response")
        if not pdpa_compliance.is_compliant:
            message_parts.append("PDPA compliance issues detected")
        if requires_escalation:
            message_parts.append("Escalation recommended")

        message = "; ".join(message_parts) if message_parts else None

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            sentiment=sentiment,
            pdpa_compliance=pdpa_compliance,
            requires_escalation=requires_escalation,
            requires_followup=requires_followup,
            message=message,
        )

    @staticmethod
    def sanitize_response(text: str) -> str:
        """
        Sanitize response to remove potential PDPA violations.

        Args:
            text: Response text to sanitize

        Returns:
            Sanitized text
        """
        from re import sub

        sensitive_patterns = [
            (r"\b\d{4}-\d{4}-\d{4}-\d{4}\b", "[CREDIT_CARD]"),
            (r"\b[A-Z]\d{7}[A-Z]\b", "[NRIC]"),
            (r"\b\d{9}\b", "[PHONE]"),
        ]

        sanitized = text
        for pattern, replacement in sensitive_patterns:
            sanitized = sub(pattern, replacement, sanitized)

        return sanitized

```

# backend/app/agent/tools/escalate_to_human.py
```py
"""Escalate to human tool for Singapore SMB Support Agent."""

from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class EscalateToHumanInput(BaseModel):
    """Input for escalate_to_human tool."""

    reason: str = Field(..., description="Reason for escalation")
    urgency: str = Field(
        default="normal",
        description="Urgency level: low, normal, high, critical",
    )
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[int] = Field(None, description="User ID (optional)")


class EscalationTicket(BaseModel):
    """Escalation ticket model."""

    ticket_id: str
    reason: str
    status: str
    assigned_to: Optional[str]
    estimated_response_time: str


class EscalateToHumanOutput(BaseModel):
    """Output for escalate_to_human tool."""

    success: bool = Field(..., description="Whether escalation was successful")
    ticket: Optional[EscalationTicket] = Field(None, description="Ticket information")
    message: str = Field(..., description="Human-readable message")


async def escalate_to_human(
    reason: str,
    urgency: str = "normal",
    session_id: str = "",
    user_id: Optional[int] = None,
    db: Optional[AsyncSession] = None,
) -> EscalateToHumanOutput:
    """
    Create a support ticket and escalate to human agent.

    Args:
        reason: Reason for escalation
        urgency: Urgency level (low, normal, high, critical)
        session_id: Session identifier
        user_id: User ID (optional)
        db: Database session (optional, for ticket creation)

    Returns:
        EscalateToHumanOutput with ticket information
    """
    try:
        from app.models.database import Conversation, SupportTicket
        from datetime import datetime

        ticket_id = f"T{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        if db and session_id:
            conversation = await db.execute(
                select(Conversation).where(Conversation.session_id == session_id)
            )
            conv = conversation.scalar_one_or_none()

            if conv:
                new_ticket = SupportTicket(
                    conversation_id=conv.id,
                    reason=reason,
                    status="open",
                )
                db.add(new_ticket)
                await db.commit()
                await db.refresh(new_ticket)

                ticket = EscalationTicket(
                    ticket_id=str(new_ticket.id),
                    reason=reason,
                    status=new_ticket.status,
                    assigned_to=None,
                    estimated_response_time="24 hours during business hours",
                )

                return EscalateToHumanOutput(
                    success=True,
                    ticket=ticket,
                    message=f"Support ticket created (ID: {new_ticket.id}). A human agent will respond within 24 hours during business hours.",
                )

        ticket = EscalationTicket(
            ticket_id=ticket_id,
            reason=reason,
            status="pending",
            assigned_to=None,
            estimated_response_time="24 hours during business hours",
        )

        return EscalateToHumanOutput(
            success=True,
            ticket=ticket,
            message=f"Escalation request created (Reference: {ticket_id}). A human agent will respond within 24 hours during business hours.",
        )

    except Exception as e:
        return EscalateToHumanOutput(
            success=False,
            ticket=None,
            message=f"Error creating escalation ticket: {str(e)}",
        )


def get_escalate_to_human_tool(db: Optional[AsyncSession] = None):
    """Factory function to create escalate_to_human tool for Pydantic AI."""
    from pydantic_ai import Tool

    async def tool_wrapper(
        reason: str,
        urgency: str = "normal",
        session_id: str = "",
        user_id: Optional[int] = None,
    ) -> dict:
        result = await escalate_to_human(
            reason=reason,
            urgency=urgency,
            session_id=session_id,
            user_id=user_id,
            db=db,
        )
        output = {
            "success": result.success,
            "ticket": result.ticket.model_dump() if result.ticket else None,
            "message": result.message,
        }
        return output

    return Tool(
        name="escalate_to_human",
        description="Escalate the conversation to a human support agent by creating a support ticket",
        function=tool_wrapper,
    )

```

# backend/app/agent/tools/__init__.py
```py

```

# backend/app/agent/tools/get_customer_info.py
```py
"""Get customer info tool for Singapore SMB Support Agent."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class GetCustomerInfoInput(BaseModel):
    """Input for get_customer_info tool."""

    customer_identifier: str = Field(
        ..., description="Customer email, phone, or customer ID"
    )
    session_id: str = Field(..., description="Session identifier")


class CustomerInfo(BaseModel):
    """Customer information model."""

    id: int
    email: str
    is_active: bool
    created_at: datetime
    data_retention_days: int


class GetCustomerInfoOutput(BaseModel):
    """Output for get_customer_info tool."""

    success: bool = Field(..., description="Whether lookup was successful")
    customer: Optional[CustomerInfo] = Field(None, description="Customer information")
    message: Optional[str] = Field(None, description="Additional information")


async def get_customer_info(
    customer_identifier: str,
    session_id: str,
    db: AsyncSession,
) -> GetCustomerInfoOutput:
    """
    Look up customer information by email, phone, or customer ID.

    Args:
        customer_identifier: Customer email, phone, or customer ID
        session_id: Session identifier for logging
        db: Database session

    Returns:
        GetCustomerInfoOutput with customer information
    """
    try:
        from app.models.database import User

        query = select(User).where(
            (User.email == customer_identifier) & (User.is_deleted == False)
        )

        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            return GetCustomerInfoOutput(
                success=False,
                customer=None,
                message=f"No customer found matching: {customer_identifier}",
            )

        customer_info = CustomerInfo(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            created_at=user.created_at,
            data_retention_days=user.data_retention_days,
        )

        return GetCustomerInfoOutput(
            success=True,
            customer=customer_info,
            message="Customer information retrieved successfully",
        )

    except Exception as e:
        return GetCustomerInfoOutput(
            success=False,
            customer=None,
            message=f"Error retrieving customer info: {str(e)}",
        )


def get_customer_info_tool(db: AsyncSession):
    """Factory function to create get_customer_info tool for Pydantic AI."""
    from pydantic_ai import Tool

    async def tool_wrapper(customer_identifier: str, session_id: str) -> dict:
        result = await get_customer_info(
            customer_identifier=customer_identifier,
            session_id=session_id,
            db=db,
        )
        if result.customer:
            output = {
                "success": result.success,
                "customer": result.customer.model_dump(),
                "message": result.message,
            }
        else:
            output = {
                "success": result.success,
                "customer": None,
                "message": result.message,
            }
        return output

    return Tool(
        name="get_customer_info",
        description="Look up customer account information using email, phone, or customer ID",
        function=tool_wrapper,
    )

```

# backend/app/agent/tools/check_business_hours.py
```py
"""Check business hours tool for Singapore SMB Support Agent."""

from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class BusinessHoursInput(BaseModel):
    """Input for check_business_hours tool."""

    date: Optional[str] = Field(
        None, description="Optional date string (YYYY-MM-DD). Defaults to today."
    )
    check_holiday: bool = Field(
        default=True, description="Whether to check for public holidays"
    )


class BusinessHoursInfo(BaseModel):
    """Business hours information model."""

    is_business_hours: bool
    is_weekend: bool
    is_public_holiday: bool
    current_time: str
    business_start: str
    business_end: str
    timezone: str
    holiday_name: Optional[str] = None


class CheckBusinessHoursOutput(BaseModel):
    """Output for check_business_hours tool."""

    success: bool = Field(..., description="Whether check was successful")
    business_hours: BusinessHoursInfo = Field(
        ..., description="Business hours information"
    )
    message: str = Field(..., description="Human-readable message")


SINGAPORE_PUBLIC_HOLIDAYS_2025 = [
    "2025-01-01",
    "2025-01-29",
    "2025-01-30",
    "2025-03-31",
    "2025-04-18",
    "2025-05-01",
    "2025-06-02",
    "2025-08-09",
    "2025-08-11",
    "2025-10-21",
    "2025-12-25",
]


async def check_business_hours(
    date: Optional[str] = None,
    check_holiday: bool = True,
    business_start: str = "09:00",
    business_end: str = "18:00",
    timezone_str: str = "Asia/Singapore",
) -> CheckBusinessHoursOutput:
    """
    Check if current time is within business hours.

    Args:
        date: Optional date string (YYYY-MM-DD). Defaults to today.
        check_holiday: Whether to check for public holidays
        business_start: Business hours start time (HH:MM)
        business_end: Business hours end time (HH:MM)
        timezone_str: Timezone string

    Returns:
        CheckBusinessHoursOutput with business hours information
    """
    try:
        from zoneinfo import ZoneInfo

        if date:
            input_date = datetime.strptime(date, "%Y-%m-%d").date()
            current_time = datetime.now(ZoneInfo(timezone_str)).replace(
                year=input_date.year,
                month=input_date.month,
                day=input_date.day,
            )
        else:
            current_time = datetime.now(ZoneInfo(timezone_str))

        is_weekend = current_time.weekday() >= 5
        is_public_holiday = False
        holiday_name = None

        if check_holiday:
            date_str = current_time.strftime("%Y-%m-%d")
            is_public_holiday = date_str in SINGAPORE_PUBLIC_HOLIDAYS_2025
            if is_public_holiday:
                holiday_name = "Singapore Public Holiday"

        start_hour, start_minute = map(int, business_start.split(":"))
        end_hour, end_minute = map(int, business_end.split(":"))

        start_minutes = start_hour * 60 + start_minute
        end_minutes = end_hour * 60 + end_minute
        current_minutes = current_time.hour * 60 + current_time.minute

        is_business_hours = (
            not is_weekend
            and not is_public_holiday
            and start_minutes <= current_minutes < end_minutes
        )

        business_info = BusinessHoursInfo(
            is_business_hours=is_business_hours,
            is_weekend=is_weekend,
            is_public_holiday=is_public_holiday,
            current_time=current_time.strftime("%Y-%m-%d %H:%M:%S"),
            business_start=business_start,
            business_end=business_end,
            timezone=timezone_str,
            holiday_name=holiday_name,
        )

        message_parts = []
        if is_weekend:
            message_parts.append("It's the weekend.")
        if is_public_holiday:
            message_parts.append(f"It's a public holiday: {holiday_name}.")
        if is_business_hours:
            message_parts.append("We're currently open for business.")
        else:
            message_parts.append("We're currently outside business hours.")
            message_parts.append(
                f"Business hours: {business_start} - {business_end} ({timezone_str})"
            )

        message = " ".join(message_parts)

        return CheckBusinessHoursOutput(
            success=True,
            business_hours=business_info,
            message=message,
        )

    except Exception as e:
        return CheckBusinessHoursOutput(
            success=False,
            business_hours=BusinessHoursInfo(
                is_business_hours=False,
                is_weekend=False,
                is_public_holiday=False,
                current_time="",
                business_start=business_start,
                business_end=business_end,
                timezone=timezone_str,
            ),
            message=f"Error checking business hours: {str(e)}",
        )


def get_check_business_hours_tool(
    business_start: str = "09:00",
    business_end: str = "18:00",
    timezone_str: str = "Asia/Singapore",
):
    """Factory function to create check_business_hours tool for Pydantic AI."""
    from pydantic_ai import Tool

    async def tool_wrapper(
        date: Optional[str] = None,
        check_holiday: bool = True,
    ) -> dict:
        result = await check_business_hours(
            date=date,
            check_holiday=check_holiday,
            business_start=business_start,
            business_end=business_end,
            timezone_str=timezone_str,
        )
        return {
            "success": result.success,
            "business_hours": result.business_hours.model_dump(),
            "message": result.message,
        }

    return Tool(
        name="check_business_hours",
        description="Check if current time is within Singapore business hours (9AM-6PM, Mon-Fri, excluding public holidays)",
        function=tool_wrapper,
    )

```

# backend/app/agent/tools/retrieve_knowledge.py
```py
"""Retrieve knowledge tool for Singapore SMB Support Agent."""

from typing import Optional
from pydantic import BaseModel, Field


class RetrieveKnowledgeInput(BaseModel):
    """Input for retrieve_knowledge tool."""

    query: str = Field(..., description="User query to search knowledge base")
    session_id: str = Field(..., description="Session identifier")


class RetrieveKnowledgeOutput(BaseModel):
    """Output for retrieve_knowledge tool."""

    success: bool = Field(..., description="Whether retrieval was successful")
    knowledge: str = Field(..., description="Retrieved knowledge text")
    sources: list[dict] = Field(default_factory=list, description="Source citations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    message: Optional[str] = Field(None, description="Additional information")


async def retrieve_knowledge(
    query: str,
    session_id: str,
    rag_pipeline=None,
) -> RetrieveKnowledgeOutput:
    """
    Retrieve relevant knowledge from the knowledge base using RAG pipeline.

    Args:
        query: User query to search for
        session_id: Session identifier for context
        rag_pipeline: RAG pipeline instance (optional, injected)

    Returns:
        RetrieveKnowledgeOutput with retrieved knowledge and metadata
    """
    if not rag_pipeline:
        return RetrieveKnowledgeOutput(
            success=False,
            knowledge="",
            sources=[],
            confidence=0.0,
            message="RAG pipeline not available",
        )

    try:
        from app.config import settings

        result = await rag_pipeline.retrieve(
            query=query,
            session_id=session_id,
            top_k=settings.RETRIEVAL_TOP_K,
        )

        if not result or not result.get("documents"):
            return RetrieveKnowledgeOutput(
                success=True,
                knowledge="No relevant information found in the knowledge base.",
                sources=[],
                confidence=0.0,
                message="Query returned no results",
            )

        knowledge_text = result.get("context", "")
        sources = result.get("metadata", [])
        confidence = result.get("confidence", 0.7)

        return RetrieveKnowledgeOutput(
            success=True,
            knowledge=knowledge_text,
            sources=sources,
            confidence=confidence,
        )

    except Exception as e:
        return RetrieveKnowledgeOutput(
            success=False,
            knowledge="",
            sources=[],
            confidence=0.0,
            message=f"Error retrieving knowledge: {str(e)}",
        )


def get_retrieve_knowledge_tool(rag_pipeline=None):
    """Factory function to create retrieve_knowledge tool for Pydantic AI."""
    from pydantic_ai import Tool

    async def tool_wrapper(query: str, session_id: str) -> dict:
        result = await retrieve_knowledge(
            query=query,
            session_id=session_id,
            rag_pipeline=rag_pipeline,
        )
        return result.model_dump()

    return Tool(
        name="retrieve_knowledge",
        description="Search knowledge base for relevant information about products, services, policies, and procedures",
        function=tool_wrapper,
    )

```

# backend/app/agent/support_agent.py
```py
"""Main Singapore SMB Support Agent using Pydantic AI."""

from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.agent.prompts.system import SYSTEM_PROMPT
from app.agent.validators import ResponseValidator, ValidationResult
from app.memory.manager import MemoryManager


class AgentContext(BaseModel):
    """Context for agent operations."""

    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[int] = Field(None, description="User ID")
    conversation_summary: str = Field(default="", description="Conversation summary")
    recent_messages: list[dict] = Field(default_factory=list, description="Recent messages")
    business_hours_status: str = Field(..., description="Current business hours status")


class AgentResponse(BaseModel):
    """Agent response model."""

    message: str = Field(..., description="Response message")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    sources: list[dict] = Field(default_factory=list, description="Source citations")
    escalated: bool = Field(default=False, description="Whether escalated to human")
    requires_followup: bool = Field(default=False, description="Whether followup needed")
    ticket_id: Optional[str] = Field(None, description="Support ticket ID if created")


class SupportAgent:
    """
    Singapore SMB Support Agent.

    Uses RAG pipeline for knowledge retrieval, memory for context,
    and Pydantic AI for tool orchestration.
    """

    def __init__(
        self,
        rag_pipeline=None,
        memory_manager: Optional[MemoryManager] = None,
        db: Optional[AsyncSession] = None,
    ):
        """
        Initialize the support agent.

        Args:
            rag_pipeline: RAG pipeline for knowledge retrieval
            memory_manager: Memory manager for session management
            db: Database session
        """
        self.rag_pipeline = rag_pipeline
        self.memory_manager = memory_manager
        self.db = db
        self.validator = ResponseValidator()

    def _get_system_prompt(self, context: AgentContext) -> str:
        """Get formatted system prompt with context."""
        return SYSTEM_PROMPT.format(
            business_hours=f"{settings.BUSINESS_HOURS_START} - {settings.BUSINESS_HOURS_END}",
            business_hours_status=context.business_hours_status,
        )

    async def _assemble_context(
        self, session_id: str, user_id: Optional[int] = None
    ) -> AgentContext:
        """Assemble agent context from memory."""
        if not self.memory_manager:
            return AgentContext(
                session_id=session_id,
                user_id=None,
                business_hours_status="unknown",
            )

        working_memory = await self.memory_manager.get_working_memory(session_id)

        from app.dependencies import BusinessContext

        business_context = BusinessContext()
        business_hours_status = "open" if business_context.is_business_hours() else "closed"

        return AgentContext(
            session_id=session_id,
            user_id=user_id,
            conversation_summary=working_memory.get("conversation_summary", ""),
            recent_messages=working_memory.get("recent_messages", []),
            business_hours_status=business_hours_status,
        )

        working_memory = await self.memory_manager.get_working_memory(session_id)

        from app.dependencies import BusinessContext

        business_context = BusinessContext()
        business_hours_status = "open" if business_context.is_business_hours() else "closed"

        return AgentContext(
            session_id=session_id,
            user_id=user_id,
            conversation_summary=working_memory.get("conversation_summary", ""),
            recent_messages=working_memory.get("recent_messages", []),
            business_hours_status=business_hours_status,
        )

    async def process_message(
        self,
        message: str,
        session_id: str,
        user_id: Optional[int] = None,
    ) -> AgentResponse:
        """
        Process a user message and generate a response.

        Args:
            message: User message
            session_id: Session identifier
            user_id: User ID (optional)

        Returns:
            AgentResponse with generated response
        """
        try:
            context = await self._assemble_context(session_id, user_id)

            validation_result = self.validator.validate_response(
                text=message,
                context={"session_id": session_id, "user_id": user_id},
            )

            if validation_result.requires_escalation:
                return await self._escalate_message(
                    message=message,
                    reason=f"Customer sentiment: {validation_result.sentiment.value}",
                    session_id=session_id,
                    user_id=user_id,
                )

            knowledge_result = None
            sources = []

            if self.rag_pipeline:
                from app.agent.tools.retrieve_knowledge import retrieve_knowledge
                from app.config import settings

                knowledge_result = await retrieve_knowledge(
                    query=message,
                    session_id=session_id,
                    rag_pipeline=self.rag_pipeline,
                )

                if knowledge_result.success:
                    sources = knowledge_result.sources

            response_text = self._generate_response(
                query=message,
                knowledge=knowledge_result.knowledge if knowledge_result else "",
                context=context,
            )

            conversation_id = None
            if self.memory_manager and user_id:
                conversation = await self.memory_manager.get_or_create_conversation(
                    session_id=session_id,
                    user_id=user_id,
                )
                conversation_id = conversation.get("id")

                if conversation_id:
                    await self.memory_manager.save_message_with_metadata(
                        session_id=session_id,
                        conversation_id=conversation_id,
                        role="user",
                        content=message,
                    )
                    await self.memory_manager.save_message_with_metadata(
                        session_id=session_id,
                        conversation_id=conversation_id,
                        role="assistant",
                        content=response_text,
                        confidence=knowledge_result.confidence if knowledge_result else 0.7,
                    )

            confidence = knowledge_result.confidence if knowledge_result else 0.7

            validation_result = self.validator.validate_response(
                text=response_text,
                confidence=confidence,
            )

            if validation_result.requires_escalation:
                return await self._escalate_message(
                    message=message,
                    reason="Low confidence or compliance issue",
                    session_id=session_id,
                    user_id=user_id,
                )

            return AgentResponse(
                message=response_text,
                confidence=confidence,
                sources=sources,
                requires_followup=validation_result.requires_followup,
                ticket_id=None,
            )

        except Exception as e:
            return AgentResponse(
                message="I apologize, but I'm experiencing a technical issue. Let me connect you with a human agent.",
                confidence=0.0,
                sources=[],
                ticket_id=None,
            )

    def _generate_response(
        self,
        query: str,
        knowledge: str,
        context: AgentContext,
    ) -> str:
        """Generate response using system prompt and knowledge."""
        if knowledge:
            return f"""Based on our knowledge base, here's what I can help you with:

{knowledge}

Is there anything else you'd like to know?"""
        else:
            return """I couldn't find specific information about your inquiry in my knowledge base. 

Could you provide more details or would you like me to connect you with a human agent who can assist you better?"""

    async def _escalate_message(
        self,
        message: str,
        reason: str,
        session_id: str,
        user_id: Optional[int] = None,
    ) -> AgentResponse:
        """Escalate message to human support."""
        from app.agent.tools.escalate_to_human import escalate_to_human

        escalation_result = await escalate_to_human(
            reason=f"{reason}. Original query: {message}",
            urgency="normal",
            session_id=session_id,
            user_id=user_id,
            db=self.db,
        )

        ticket_id = None
        if escalation_result.ticket:
            ticket_id = escalation_result.ticket.ticket_id

        return AgentResponse(
            message=escalation_result.message,
            confidence=1.0,
            sources=[],
            escalated=True,
            ticket_id=ticket_id,
        )


async def get_support_agent(
    rag_pipeline=None,
    memory_manager: Optional[MemoryManager] = None,
    db: Optional[AsyncSession] = None,
) -> SupportAgent:
    """Factory function to create support agent instance."""
    return SupportAgent(
        rag_pipeline=rag_pipeline,
        memory_manager=memory_manager,
        db=db,
    )

```

# backend/app/services/__init__.py
```py

```

# backend/app/alembic/env.py
```py
"""Alembic configuration for database migrations."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.models.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_engine():
    """Get database engine from configuration."""
    return engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```

# backend/app/api/__init__.py
```py

```

# backend/app/api/routes/__init__.py
```py

```

# backend/app/api/routes/auth.py
```py
"""Authentication API routes for Singapore SMB Support Agent (MVP - Session-based)."""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_memory_manager
from app.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.models.database import User, Conversation
from app.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    Args:
        request: User registration data
        db: Database session

    Returns:
        UserResponse with created user information
    """
    try:
        existing_user = await db.execute(
            select(User).where(User.email == request.email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        hashed_password = pwd_context.hash(request.password)

        new_user = User(
            email=request.email,
            hashed_password=hashed_password,
            consent_given_at=datetime.utcnow(),
            consent_version="v1.0",
            data_retention_days=settings.PDPA_DATA_RETENTION_DAYS,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
    memory_manager=Depends(get_memory_manager),
):
    """
    Login a user and create a session.

    Args:
        request: User login credentials
        db: Database session
        memory_manager: Memory manager for session creation

    Returns:
        TokenResponse with session token
    """
    try:
        from passlib.context import CryptContext
        from uuid import uuid4

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()

        if not user or not pwd_context.verify(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive",
            )

        session_id = str(uuid4())

        new_conversation = Conversation(
            user_id=user.id,
            session_id=session_id,
            language="en",
        )

        db.add(new_conversation)
        await db.commit()

        session_data = {
            "user_id": user.id,
            "email": user.email,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
        }

        await memory_manager.save_session(session_id, session_data)

        return TokenResponse(
            access_token=session_id,
            token_type="session",
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}",
        )


@router.post("/logout")
async def logout(
    session_id: str,
    memory_manager=Depends(get_memory_manager),
):
    """
    Logout a user by ending their session.

    Args:
        session_id: Session identifier
        memory_manager: Memory manager for session cleanup

    Returns:
        Success message
    """
    try:
        session_data = await memory_manager.get_session(session_id)

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        await memory_manager.save_session(session_id, {})

        return {"message": "Logged out successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user information from session.

    Args:
        session_id: Session identifier
        db: Database session

    Returns:
        UserResponse with current user information
    """
    try:
        from sqlalchemy import text

        result = await db.execute(
            text("""SELECT u.id, u.email, u.is_active, u.created_at
                   FROM users u 
                   JOIN conversations c ON u.id = c.user_id 
                   WHERE c.session_id = :session_id AND u.is_active = TRUE"""),
            {"session_id": session_id},
        )
        user = result.fetchone()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return UserResponse(
            id=user[0],
            email=user[1],
            is_active=user[2],
            created_at=user[3],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}",
        )


@router.post("/session/new")
async def create_new_session(
    session_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    memory_manager=Depends(get_memory_manager),
):
    """
    Create a new chat session (MVP - simplified version).

    Args:
        session_id: Optional existing session ID
        db: Database session
        memory_manager: Memory manager for session creation

    Returns:
        Session information
    """
    try:
        from uuid import uuid4

        new_session_id = str(uuid4())

        session_data = {
            "user_id": None,
            "email": None,
            "created_at": datetime.utcnow().isoformat(),
            "messages": [],
        }

        await memory_manager.save_session(new_session_id, session_data)

        return {
            "session_id": new_session_id,
            "message": "New session created",
            "expires_in": f"{settings.PDPA_SESSION_TTL_MINUTES} minutes",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}",
        )

```

# backend/app/api/routes/chat.py
```py
"""Chat API routes with WebSocket support for Singapore SMB Support Agent."""

from typing import Optional
from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_memory_manager, get_session_data
from app.models.schemas import ChatRequest, ChatResponse, SourceCitation
from app.agent.support_agent import SupportAgent, get_support_agent


router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer(auto_error=False)


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept a WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(
        self,
        session_id: str,
        message: dict,
    ):
        """Send a message to a specific session."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)


manager = ConnectionManager()


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    memory_manager=Depends(get_memory_manager),
    token: Optional[str] = Depends(security),
):
    """
    Process a chat message using the support agent.

    Args:
        request: Chat request with message and session_id
        db: Database session
        memory_manager: Memory manager instance
        token: Optional authentication token

    Returns:
        ChatResponse with agent response
    """
    try:
        session_data = await memory_manager.get_session(request.session_id)

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found. Please start a new session.",
            )

        user_id = session_data.get("user_id")

        agent = await get_support_agent(
            rag_pipeline=None,
            memory_manager=memory_manager,
            db=db,
        )

        response = await agent.process_message(
            message=request.message,
            session_id=request.session_id,
            user_id=user_id,
        )

        source_citations = [
            SourceCitation(
                content=source.get("content", ""),
                metadata=source.get("metadata", {}),
                score=source.get("score", 0.0),
            )
            for source in response.sources
        ]

        return ChatResponse(
            session_id=request.session_id,
            message=response.message,
            confidence=response.confidence,
            sources=source_citations,
            requires_followup=response.requires_followup,
            escalated=response.escalated,
            ticket_id=response.ticket_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}",
        )


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time chat.

    Args:
        websocket: WebSocket connection
        db: Database session
    """
    session_id = None

    try:
        session_id = websocket.query_params.get("session_id")
        if not session_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        memory_manager = await get_memory_manager(db)

        session_data = await memory_manager.get_session(session_id)
        if not session_data:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": "Session not found. Please start a new session.",
                }
            )
            await websocket.close()
            return

        await manager.connect(session_id, websocket)

        agent = await get_support_agent(
            rag_pipeline=None,
            memory_manager=memory_manager,
            db=db,
        )

        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to support agent",
                "session_id": session_id,
            }
        )

        while True:
            data = await websocket.receive_json()

            message_type = data.get("type", "message")
            message_content = data.get("message", "")

            if message_type == "message":
                if not message_content:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": "Message cannot be empty",
                        }
                    )
                    continue

                user_id = session_data.get("user_id")

                response = await agent.process_message(
                    message=message_content,
                    session_id=session_id,
                    user_id=user_id,
                )

                await websocket.send_json(
                    {
                        "type": "response",
                        "session_id": session_id,
                        "message": response.message,
                        "confidence": response.confidence,
                        "sources": response.sources,
                        "requires_followup": response.requires_followup,
                        "escalated": response.escalated,
                        "ticket_id": response.ticket_id,
                    }
                )

            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif message_type == "disconnect":
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        if session_id and session_id in manager.active_connections:
            await manager.active_connections[session_id].send_json(
                {
                    "type": "error",
                    "message": f"Error: {str(e)}",
                }
            )
    finally:
        if session_id:
            manager.disconnect(session_id)


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    memory_manager=Depends(get_memory_manager),
    token: Optional[str] = Depends(security),
):
    """
    Get session information.

    Args:
        session_id: Session identifier
        memory_manager: Memory manager instance
        token: Optional authentication token

    Returns:
        Session data
    """
    try:
        session_data = await memory_manager.get_session(session_id)

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )

        return {
            "session_id": session_id,
            "messages": session_data.get("messages", []),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session: {str(e)}",
        )

```

# backend/app/models/__init__.py
```py

```

# backend/app/models/database.py
```py
"""SQLAlchemy database models for Singapore SMB Support Agent."""

from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for database models."""

    pass


class User(Base):
    """User account model with PDPA compliance fields."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    consent_given_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    consent_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1.0")

    data_retention_days: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    auto_expiry_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Conversation(Base):
    """Conversation session model."""

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    summary_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    summaries: Mapped[list["ConversationSummary"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )
    tickets: Mapped[list["SupportTicket"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), nullable=False, index=True
    )

    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    sources: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class ConversationSummary(Base):
    """LLM-generated conversation summaries for context compression."""

    __tablename__ = "conversation_summaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), nullable=False, index=True
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    message_range_start: Mapped[int] = mapped_column(Integer, nullable=False)
    message_range_end: Mapped[int] = mapped_column(Integer, nullable=False)

    embedding_vector: Mapped[bytes | None] = mapped_column(Text, nullable=True)

    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(back_populates="summaries")


class SupportTicket(Base):
    """Human escalation tickets."""

    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"), nullable=False, index=True
    )

    reason: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")

    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="tickets")

```

# backend/app/models/domain.py
```py
"""Domain models for Singapore SMB Support Agent."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationLanguage(str, Enum):
    ENGLISH = "en"
    MANDARIN = "zh"
    MALAY = "ms"
    TAMIL = "ta"


class TicketStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class User(BaseModel):
    id: int
    email: str
    consent_given_at: datetime
    consent_version: str
    data_retention_days: int = 30
    auto_expiry_at: Optional[datetime] = None
    is_active: bool = True
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime


class Conversation(BaseModel):
    id: int
    user_id: int
    session_id: str
    language: ConversationLanguage = ConversationLanguage.ENGLISH
    is_active: bool = True
    ended_at: Optional[datetime] = None
    summary_count: int = 0
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    confidence: Optional[float] = None
    sources: Optional[str] = None
    created_at: datetime


class ConversationSummary(BaseModel):
    id: int
    conversation_id: int
    summary: str
    message_range_start: int
    message_range_end: int
    embedding_vector: Optional[bytes] = None
    metadata: Optional[str] = None
    created_at: datetime


class SupportTicket(BaseModel):
    id: int
    conversation_id: int
    reason: str
    status: TicketStatus = TicketStatus.OPEN
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

```

# backend/app/models/schemas.py
```py
"""API Pydantic schemas for Singapore SMB Support Agent."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=8, max_length=128, description="User password"
    )
    consent_given: bool = Field(default=True, description="PDPA consent given")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SourceCitation(BaseModel):
    content: str
    metadata: dict
    score: float


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    language: str = Field(default="en", description="Message language (en, zh, ms, ta)")


class ChatResponse(BaseModel):
    session_id: str
    message: str
    role: str = "assistant"
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: List[SourceCitation] = Field(default_factory=list)
    requires_followup: bool = False
    escalated: bool = False
    ticket_id: Optional[str] = None


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: dict


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SupportResponse(BaseModel):
    """Support agent response for internal use."""

    message: str = Field(..., description="Response message")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    sources: List[SourceCitation] = Field(
        default_factory=list, description="Source citations"
    )
    escalated: bool = Field(default=False, description="Whether escalated to human")
    requires_followup: bool = Field(
        default=False, description="Whether followup needed"
    )
    ticket_id: Optional[str] = Field(None, description="Support ticket ID if created")

```

# backend/data/policies/privacy_policy.md
```md
# Privacy Policy

## Effective Date: January 1, 2025

## Information We Collect

We collect the following types of information:
- **Personal Information**: Name, email address, phone number, billing information
- **Usage Information**: Login history, feature usage, page views
- **Device Information**: IP address, browser type, operating system
- **Cookies and Tracking**: For analytics and personalization

## How We Use Your Information

Your information is used to:
- Provide and improve our services
- Process transactions and send billing information
- Send relevant communications (with your consent)
- Prevent fraud and ensure security
- Comply with legal obligations

## Data Security

We implement industry-standard security measures:
- Encryption in transit and at rest
- Regular security audits
- Access controls and authentication
- Secure data centers

## Your Rights

You have the right to:
- Access your personal data
- Correct inaccurate information
- Delete your account and data
- Opt out of marketing communications
- Data portability

## Third-Party Sharing

We do not sell your personal information. We may share data with:
- Service providers who assist our operations
- Legal authorities when required by law
- Business partners with your explicit consent

## Cookies Policy

We use cookies for:
- Essential functionality
- Analytics and performance
- Personalization
- Advertising (with your consent)

You can manage cookie preferences in your browser settings.

## Children's Privacy

Our services are not intended for children under 13. We do not knowingly collect personal information from children.

## International Data Transfers

Your data may be transferred and processed in countries other than your own. We ensure appropriate safeguards are in place.

## Policy Updates

We may update this policy from time to time. We will notify customers of significant changes via email.

## Contact Us

For privacy-related inquiries, contact us at:
- Email: privacy@example.com
- Address: 123 Privacy Lane, Data City, DC 12345
```

# backend/data/policies/shipping_policy.md
```md
# Shipping Policy

## Effective Date: January 1, 2025

## Shipping Destinations

### Domestic Shipping (United States)
We ship to all 50 states, including:
- Standard shipping available everywhere
- Express and next-day available to most locations
- Alaska and Hawaii may have extended delivery times

### International Shipping
We ship to over 100 countries worldwide. Popular destinations include:
- Canada, Mexico, UK, Europe
- Australia, New Zealand
- Asia (select countries)
- South America (select countries)

## Shipping Options & Rates

### Domestic Shipping
| Option | Delivery Time | Cost |
|--------|--------------|------|
| Standard | 5-7 business days | $4.99 (Free over $50) |
| Express | 2-3 business days | $9.99 |
| Next-Day | 1 business day | $19.99 |
| Weekend Delivery | Sat/Sun delivery | $24.99 |

### International Shipping
| Option | Delivery Time | Cost |
|--------|--------------|------|
| International Standard | 10-15 business days | Calculated at checkout |
| International Express | 5-7 business days | Calculated at checkout |

International rates vary by destination, weight, and package size.

## Order Processing Time

- **In-stock items**: 1-2 business days before shipping
- **Personalized/custom items**: 3-5 business days before shipping
- **Pre-orders**: Ships on release date (you'll be notified)
- **Backorders**: You'll be notified of estimated ship date

Processing time is separate from shipping time. Total delivery time = processing + shipping.

## Tracking Your Order

### When Tracking is Available
You'll receive tracking information when:
- Your order ships from our warehouse
- Items may ship separately for multi-item orders
- Each shipment will have its own tracking number

### How to Track
1. Check your email for shipping confirmation
2. Log into your account → Order History
3. Enter tracking number on carrier's website
4. Use our website's "Track Order" page

## Delivery Issues

### Delayed Shipments
If your shipment is delayed:
- We'll notify you via email with new estimate
- You can request cancellation if delay exceeds 7 days
- Expedited shipping may be upgraded at no extra cost

### Lost Packages
If tracking shows no movement for 7 days:
- Contact us immediately
- We'll file claim with carrier
- Replacement or refund will be processed promptly

### Damaged Shipments
If package arrives damaged:
- Take photos of damage
- Keep all packaging
- Contact us within 48 hours
- We'll arrange return and replacement

## Delivery Instructions

### Special Instructions
At checkout, you can specify:
- "Leave at door"
- "Require signature"
- "Leave with neighbor"
- Specific delivery notes

We'll do our best to accommodate carrier policies.

### Failed Delivery Attempts
If delivery fails:
- Carrier will leave notice
- Second attempt within 1-2 business days
- Third attempt within 2-3 business days
- Package returned after 3 failed attempts

## Address Changes

### Before Shipping
- Within 2 hours of order: Free change
- 2-24 hours after order: May incur small fee
- After 24 hours: Cannot guarantee changes

### After Shipping
- Address changes cannot be made
- You'll need to refuse delivery
- Contact us for return/replacement process

## Shipping Restrictions

### Items That Cannot Be Shipped
- Hazardous materials
- Oversized or extremely heavy items
- Perishable goods (select items only)
- Items prohibited by law

### International Restrictions
Some items cannot be shipped internationally due to:
- Export regulations
- Import restrictions
- Carrier limitations
- Size/weight constraints

## Holidays and Peak Seasons

### Holiday Schedule
During major holidays, shipping may be delayed:
- Thanksgiving week
- Christmas/New Year period
- Other major US holidays

We'll post holiday shipping cutoffs on our homepage.

### Peak Season Delays
Peak seasons may experience delays:
- Black Friday/Cyber Monday
- Back-to-school season
- Major sales events

Order early for guaranteed delivery.

## Shipping to Multiple Addresses

You can ship items to multiple addresses:
- Add all items to cart
- Select "Ship to multiple addresses" at checkout
- Assign items to different addresses
- Shipping calculated per address

Each address counts as a separate order for shipping purposes.

## Business Shipping

### Business Accounts
Business accounts receive:
- Volume shipping discounts
- Consolidated shipping options
- Account management
- Net payment terms available

Contact our business sales team to set up an account.

## International Customs

### Duties and Taxes
- International orders may incur customs duties
- These fees are customer's responsibility
- We cannot prepay customs fees
- Check your country's import regulations

### Customs Processing
- International orders may be held for customs inspection
- This can add 1-5 days to delivery time
- Carrier will contact you if additional information needed
- We cannot expedite customs clearance

## Questions and Support

### Contact Information
- **Shipping Email**: shipping@example.com
- **Phone**: 1-800-SHIP-IT (1-800-744-7488)
- **Live Chat**: Available on our website
- **Support Hours**: Mon-Fri 9AM-8PM EST

### Common Questions
- **Can I pick up my order?** No, we don't offer local pickup
- **Can I rush my order?** Yes, call us to discuss expedited options
- **Do you ship to PO boxes?** Yes, via standard shipping only
- **Can I change shipping method after ordering?** Only before shipping

## Policy Updates

We reserve the right to modify shipping policies and rates. Changes will be posted on our website and major changes will be emailed to customers.
```

# backend/data/policies/terms_of_service.md
```md
# Terms of Service

## Effective Date: January 1, 2025

## Acceptance of Terms

By accessing or using our services, you agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, you may not use our services.

## Description of Services

We provide a comprehensive suite of business solutions including:
- Cloud infrastructure and hosting
- Software applications and tools
- API integrations
- Data analytics services
- Custom development solutions
- Consulting services

## Account Registration

### Creating an Account
To use our services, you must:
- Be at least 18 years old
- Provide accurate and complete information
- Maintain and update your account information
- Keep your password secure

### Account Responsibilities
You are responsible for:
- All activities that occur under your account
- Maintaining the confidentiality of your password
- Notifying us immediately of unauthorized access
- Compliance with these Terms by anyone using your account

## Subscription and Billing

### Subscription Plans
We offer various subscription plans with different features and pricing. All plans auto-renew unless cancelled before the renewal date.

### Payment Terms
- You agree to pay all charges incurred under your account
- Payments are processed in US Dollars
- Prices are subject to change with 30-day notice
- We reserve the right to suspend services for non-payment

### Refund Policy
Our refund policy is available separately. By subscribing, you acknowledge and agree to the refund policy terms.

## Service Availability and Uptime

### Uptime Commitment
We strive for 99.9% uptime for standard plans and 99.99% for enterprise plans.

### Scheduled Maintenance
We may perform scheduled maintenance with advance notice. Maintenance may cause temporary service interruptions.

### Service Modifications
We reserve the right to modify, suspend, or discontinue services with reasonable notice.

## Acceptable Use Policy

### Permitted Use
You may use our services for:
- Legitimate business purposes
- Compliance with applicable laws and regulations
- Activities that do not harm our systems or other users

### Prohibited Activities
You may NOT:
- Use services for illegal or unauthorized purposes
- Attempt to gain unauthorized access to our systems
- Interfere with or disrupt service operation
- Transmit viruses, malware, or malicious code
- Violate intellectual property rights
- Harass, abuse, or harm other users
- Engage in fraudulent activities
- Exceed authorized usage limits

### Violation Consequences
Violations may result in:
- Warning or notice of violation
- Temporary or permanent service suspension
- Account termination
- Legal action if appropriate

## Intellectual Property

### Our Intellectual Property
All content, features, and functionality are owned by us or our licensors and protected by intellectual property laws.

### Your Content
You retain ownership of content you provide. You grant us a license to use, store, and process your content to provide services.

### User-Generated Content
By submitting content, you represent that:
- You own or have permission to use the content
- The content does not violate any laws or third-party rights
- The content is accurate and not misleading

## Privacy and Data Protection

### Privacy Policy
Your use of our services is also governed by our Privacy Policy, which describes how we collect, use, and protect your information.

### Data Security
We implement reasonable security measures to protect your data. However, no system is completely secure, and you acknowledge the inherent risks.

### Data Backup
We perform regular data backups but do not guarantee data will never be lost. You are responsible for backing up critical data.

## Limitation of Liability

### Disclaimer of Warranties
Services are provided "as is" without warranties of any kind, either express or implied.

### Limitation of Damages
To the maximum extent permitted by law, we shall not be liable for:
- Indirect, incidental, special, or consequential damages
- Lost profits or business interruption
- Loss of data or information
- Damages exceeding the fees paid in the past 12 months

### Maximum Liability
Our total liability to you shall not exceed the amount you have paid to us in the 12 months preceding the claim.

## Indemnification

You agree to indemnify and hold us harmless from:
- Claims arising from your use of services
- Claims related to your content
- Claims related to your violation of these Terms
- Expenses (including legal fees) related to such claims

## Termination

### Termination by You
You may terminate your account at any time. Your access will end at the end of the current billing period.

### Termination by Us
We may terminate or suspend your account for:
- Violation of these Terms
- Non-payment
- Extended inactivity
- Suspension of our services

### Effect of Termination
Upon termination:
- Your right to use services ends immediately
- You remain liable for all incurred charges
- We may delete your data (we'll provide export option)
- Certain provisions survive termination

## Governing Law and Dispute Resolution

### Governing Law
These Terms are governed by the laws of the United States and the state where our company is headquartered.

### Arbitration
Disputes shall be resolved through binding arbitration, except for claims that may be brought in small claims court.

### Class Action Waiver
You agree to resolve disputes individually and waive any right to participate in class actions or class-wide arbitrations.

## Modifications to Terms

### Right to Modify
We reserve the right to modify these Terms at any time. Modifications will be effective upon posting.

### Notice of Changes
We will provide notice of material changes via:
- Email notification
- In-app notification
- Posting on our website

### Continued Use
Continued use of services after changes constitutes acceptance of modified Terms.

## Miscellaneous

### Entire Agreement
These Terms constitute the entire agreement between you and us regarding our services.

### Severability
If any provision is deemed unenforceable, the remaining provisions remain in effect.

### Waiver
Failure to enforce any provision does not constitute a waiver of that provision.

### Assignment
You may not assign these Terms without our consent. We may assign without restriction.

### Force Majeure
We are not liable for failures due to events beyond our control (natural disasters, wars, etc.).

## Contact Information

For questions about these Terms:
- **Email**: legal@example.com
- **Address**: Legal Department, 123 Legal Street, Corporate City, CC 12345
- **Phone**: 1-800-LEGAL-01 (1-800-534-2501)

## Additional Terms for Specific Services

Certain services may have additional terms that supplement these Terms. By using those services, you also agree to those additional terms.

---

Last Updated: January 1, 2025
```

# backend/data/policies/return_policy.md
```md
# Return Policy

## Last Updated: December 15, 2025

## Overview

We want you to be completely satisfied with your purchase. If you're not happy for any reason, we're here to help.

## 30-Day Satisfaction Guarantee

All purchases come with a 30-day satisfaction guarantee. If you're not satisfied within 30 days of purchase, you may request a full refund.

## Eligible Items

### Fully Refundable
- All physical products in original condition
- Software licenses (within 30 days)
- Subscription services (pro-rated refund available)

### Non-Refundable
- Gift cards
- Custom or personalized items
- Digital downloads once accessed
- Items marked as "Final Sale"

## Return Process

### Step 1: Initiate Return
- Log into your account
- Navigate to Order History
- Select the order and items to return
- Choose refund or exchange

### Step 2: Pack Items
- Use original packaging when possible
- Include all accessories and documentation
- Remove personal data from devices

### Step 3: Ship Return
- Use provided prepaid label (for defective/incorrect items)
- Use your preferred carrier (for customer preference returns)
- Obtain tracking number

### Step 4: Receive Refund
- We process returns within 2-3 business days of receipt
- Refund timing depends on your payment method
- You'll receive email confirmation when processed

## Refund Methods

Refunds are issued to the original payment method:
- **Credit Card**: 5-7 business days
- **PayPal**: 3-5 business days
- **Bank Transfer**: 7-10 business days
- **Store Credit**: Immediate

## Exchange Policy

Exchanges are available for:
- Different size/color of same product
- Different product of equal or greater value
- Upgrade to premium version

Pay difference for higher-priced items or receive credit for lower-priced exchanges.

## Damaged or Defective Items

If you receive a damaged or defective item:
- Contact us within 48 hours of delivery
- Provide photos of damage/defect
- We'll ship replacement or issue full refund
- Return shipping is prepaid by us

## Return Shipping

### When We Pay
- Items arrived damaged or defective
- Incorrect item was shipped
- Manufacturing defect discovered

### When You Pay
- Change of mind or personal preference
- Accidentally ordered wrong item
- Item no longer needed

## Restocking Fees

No restocking fees for standard returns. Special circumstances may incur fees (we'll notify you before processing).

## Final Sale Items

Items marked "Final Sale" cannot be returned or exchanged unless defective. These are clearly marked during checkout.

## International Returns

International customers may return items, but are responsible for:
- Return shipping costs
- Customs fees and duties
- Potential additional taxes

## Exceptions and Special Cases

### Software Licenses
- Can be returned within 30 days if not activated
- Cannot be returned after activation or use

### Subscription Services
- Pro-rated refund available for unused portion
- Cancel anytime, access continues until billing period ends

### Bulk Orders
- Custom return policy applies for orders over 50 units
- Contact our sales team for details

## How to Contact Us

For return-related questions:
- **Email**: returns@example.com
- **Phone**: 1-800-RETURNS (1-800-738-8767)
- **Live Chat**: Available on our website
- **Hours**: Mon-Fri 9AM-8PM EST, Sat 10AM-6PM EST

## Policy Changes

We reserve the right to modify this policy. Changes will be posted online and major changes will be emailed to customers.
```

# backend/data/products/product_catalog.md
```md
# Product Catalog

## Featured Products

### Professional Analytics Dashboard
- **SKU**: PRO-AN-001
- **Price**: $199/year
- **Features**: Real-time analytics, custom reports, API access, unlimited users
- **Best for**: Medium to large businesses

### Starter CRM Package
- **SKU**: STR-CRM-001
- **Price**: $99/year
- **Features**: Contact management, email integration, basic reporting
- **Best for**: Small businesses and startups

### Enterprise Integration Suite
- **SKU**: ENT-INT-001
- **Price**: Custom pricing
- **Features**: Multi-system integration, dedicated support, custom development
- **Best for**: Large enterprises with complex needs

### Social Media Manager
- **SKU**: SOC-MED-001
- **Price**: $79/year
- **Features**: Schedule posts, analytics, multi-platform support
- **Best for**: Marketing teams and agencies

### E-commerce Platform
- **SKU**: ECOM-PLAT-001
- **Price**: $149/year
- **Features**: Product catalog, payment processing, inventory management
- **Best for**: Online retailers

## Product Specifications

### System Requirements
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Stable internet connection
- JavaScript enabled

### Integrations
- Salesforce
- HubSpot
- Slack
- Microsoft Teams
- QuickBooks
- Xero

### Support Included
All products include:
- Email support (24-48 hour response)
- Knowledge base access
- Community forums
- Regular updates and improvements

## Product Comparison

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Users | Up to 5 | Unlimited | Unlimited |
| Storage | 10GB | 100GB | Unlimited |
| API Access | No | Yes | Yes |
| Custom Reports | Basic | Advanced | Unlimited |
| Dedicated Support | No | No | Yes |
| SLA | 99% | 99.9% | 99.99% |

## New Releases

### Version 3.0 (Latest Release)
- Enhanced performance and speed
- New AI-powered insights
- Improved mobile experience
- Additional security features
- Expanded integration options

Release date: December 2025
```

# backend/data/faq/03_services_overview.md
```md
# Services Overview

## What services do you offer?

We provide comprehensive business solutions including:
- **Cloud Infrastructure**: Scalable cloud hosting and deployment services
- **API Integration**: Seamless integration with popular third-party services
- **Data Analytics**: Advanced analytics and reporting tools
- **Custom Development**: Tailored software solutions for your specific needs
- **Consulting**: Expert advice on digital transformation and optimization

## Is setup included?

Yes, all plans include free initial setup and onboarding. Our team will help you get started and ensure everything is configured correctly.

## Do you provide training?

We offer various training options:
- Self-paced video tutorials (included in all plans)
- Live webinars (Professional plan and above)
- On-site training (Enterprise plan)

## What is your SLA?

We maintain a 99.9% uptime SLA for all our services. Enterprise customers receive a 99.99% uptime guarantee with financial penalties for downtime.

## Can I get a custom solution?

Absolutely! For businesses with unique requirements, we can create custom solutions. Contact our sales team for a consultation.
```

# backend/data/faq/02_business_hours.md
```md
# Business Hours

## What are your support hours?

Our support team is available:
- **Monday to Friday**: 9:00 AM - 8:00 PM EST
- **Saturday**: 10:00 AM - 6:00 PM EST
- **Sunday**: 12:00 PM - 4:00 PM EST

## Do you offer 24/7 support for enterprise customers?

Yes, enterprise customers with the Enterprise plan have access to 24/7 priority support with guaranteed response times.

## What about holidays?

We observe major US holidays. During these days, support hours may be reduced. We'll notify customers in advance of any holiday schedule changes.

## What time zone are your hours based on?

All support hours are in Eastern Standard Time (EST). We recommend checking current time in EST when planning to contact us.

## Can I schedule a callback?

Yes, you can request a callback through our online portal. We'll call you back within your selected time window during our business hours.
```

# backend/data/faq/01_pricing.md
```md
# Pricing FAQ

## What are your standard pricing plans?

We offer three pricing tiers:
- **Basic Plan**: $29/month for small businesses
- **Professional Plan**: $79/month for growing businesses
- **Enterprise Plan**: Custom pricing for large organizations

## What payment methods do you accept?

We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers for annual plans.

## Do you offer refunds?

Yes, we offer a 30-day money-back guarantee on all plans. If you're not satisfied within the first 30 days, you can request a full refund.

## Are there any hidden fees?

No, we believe in transparent pricing. All features listed in each plan are included with no hidden fees or surprise charges.

## Can I change my plan later?

Yes, you can upgrade or downgrade your plan at any time. When upgrading, you'll pay prorated fees for the current billing period.
```

# backend/data/faq/04_returns_refunds.md
```md
# Returns and Refunds

## What is your return policy?

We offer a 30-day satisfaction guarantee on all products. If you're not completely satisfied, you can return the product within 30 days of purchase for a full refund.

## How do I initiate a return?

To initiate a return:
1. Log into your account
2. Go to Order History
3. Select the order containing the item you want to return
4. Click "Request Return"
5. Follow the instructions provided

## What items are non-returnable?

Digital products, gift cards, and personalized items cannot be returned. Physical products must be in their original packaging and unused condition.

## How long does a refund take?

Once we receive and process your return (typically 2-3 business days), refunds are issued:
- Credit card: 5-7 business days
- PayPal: 3-5 business days
- Bank transfer: 7-10 business days

## Who pays for return shipping?

For defective or incorrect items, we provide a prepaid shipping label. For returns due to customer preference, return shipping costs are the customer's responsibility.

## Can I exchange instead of refund?

Yes, exchanges are available. If you'd prefer a different product, you can select an exchange during the return process. We'll ship the new item once the original is received.
```

# backend/data/faq/05_shipping_delivery.md
```md
# Shipping and Delivery

## What shipping options do you offer?

We provide several shipping options:
- **Standard Shipping**: 5-7 business days (Free on orders over $50)
- **Express Shipping**: 2-3 business days ($9.99)
- **Next-Day Shipping**: 1 business day ($19.99)

## Do you ship internationally?

Yes, we ship to over 100 countries worldwide. International shipping rates and delivery times vary by destination.

## How do I track my order?

Once your order ships, you'll receive an email with a tracking number. You can also track your order by logging into your account and viewing Order History.

## What if my package is lost or damaged?

If your package is lost or damaged during transit, please contact us immediately. We'll either ship a replacement or issue a full refund, whichever you prefer.

## Can I change my shipping address after ordering?

Address changes are possible within 2 hours of placing your order. After that time, we cannot guarantee modifications as the order may already be in process.

## Do you offer weekend delivery?

Weekend delivery is available in select areas for Next-Day Shipping. Select this option at checkout if available in your area.
```

# backend/scripts/ingest_documents.py
```py
"""CLI tool for document ingestion into Qdrant vector database."""

import asyncio
import argparse
import json
from pathlib import Path
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion.pipeline import IngestionPipeline, IngestionResult
from app.rag.qdrant_client import QdrantManager


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Ingest documents into Qdrant vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest single file
  python -m backend.scripts.ingest_documents --input-files document.pdf

  # Ingest multiple files
  python -m backend.scripts.ingest_documents --input-files file1.pdf,file2.docx

  # Ingest entire directory
  python -m backend.scripts.ingest_documents --input-dir ./documents

  # Ingest directory recursively
  python -m backend.scripts.ingest_documents --input-dir ./documents --recursive

  # Use recursive chunking strategy
  python -m backend.scripts.ingest_documents --input-dir ./documents --chunk-strategy recursive

  # Ingest with custom collection name
  python -m backend.scripts.ingest_documents --input-dir ./documents --collection custom_kb
        """,
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input-files",
        type=str,
        help="Comma-separated list of file paths to ingest",
    )
    input_group.add_argument(
        "--input-dir",
        type=str,
        help="Directory path containing documents to ingest",
    )

    parser.add_argument(
        "--collection",
        type=str,
        default="knowledge_base",
        help="Qdrant collection name (default: knowledge_base)",
    )
    parser.add_argument(
        "--chunk-strategy",
        type=str,
        choices=["semantic", "recursive"],
        default="semantic",
        help="Chunking strategy (default: semantic)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of concurrent document ingestions (default: 10)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively scan input directory for documents",
    )
    parser.add_argument(
        "--file-extensions",
        type=str,
        default=None,
        help="Comma-separated list of file extensions to process (default: all supported)",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default=None,
        help="JSON string with additional metadata to add to all documents",
    )
    parser.add_argument(
        "--init-collections",
        action="store_true",
        help="Initialize Qdrant collections before ingestion",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--use-mock-embeddings",
        action="store_true",
        help="Use mock embeddings instead of real API (for testing)",
    )

    return parser.parse_args()


def parse_metadata(metadata_str: str) -> Optional[dict]:
    """Parse metadata JSON string."""
    if not metadata_str:
        return None

    try:
        return json.loads(metadata_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing metadata JSON: {e}")
        return None

    try:
        import json

        return json.loads(metadata_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing metadata JSON: {e}")
        return None

    try:
        import json

        return json.loads(metadata_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing metadata JSON: {e}")
        return None


async def ingest_single_file(
    file_path: str,
    pipeline: IngestionPipeline,
    verbose: bool = False,
) -> dict:
    """Ingest a single document."""
    print(f"Processing: {file_path}")
    result = await pipeline.ingest_document(file_path)

    if verbose or not result.get("success"):
        print(f"  Result: {result.get('success')}")
        if not result.get("success"):
            print(f"  Error: {result.get('error')}")
        else:
            print(f"  Chunks: {result.get('chunks_processed', 0)}")
            print(f"  Points: {result.get('points_upserted', 0)}")

    return result


async def ingest_files(
    file_paths: list[str],
    pipeline: IngestionPipeline,
    batch_size: int,
    verbose: bool = False,
) -> IngestionResult:
    """Ingest multiple files."""
    print(f"\nProcessing {len(file_paths)} files (batch size: {batch_size})")
    print("=" * 80)

    result = await pipeline.ingest_batch(
        file_paths=file_paths,
        batch_size=batch_size,
    )

    return result


async def ingest_directory(
    directory_path: str,
    pipeline: IngestionPipeline,
    recursive: bool,
    batch_size: int,
    file_extensions: Optional[list[str]] = None,
    verbose: bool = False,
) -> IngestionResult:
    """Ingest all documents from a directory."""
    print(f"\nProcessing directory: {directory_path}")
    if recursive:
        print(f"Recursive scan: enabled")
    print("=" * 80)

    result = await pipeline.ingest_directory(
        directory_path=directory_path,
        recursive=recursive,
        batch_size=batch_size,
        file_extensions=file_extensions,
    )

    return result


def print_summary(result: IngestionResult):
    """Print ingestion summary."""
    print("\n" + "=" * 80)
    print("INGESTION SUMMARY")
    print("=" * 80)
    print(f"Total Documents: {result.total_documents}")
    print(f"Successful: {result.successful}")
    print(f"Failed: {result.failed}")
    print(f"Total Chunks: {result.total_chunks}")

    if result.errors:
        print("\nErrors:")
        for i, error in enumerate(result.errors[:10], 1):
            print(f"  {i}. {error}")
        if len(result.errors) > 10:
            print(f"  ... and {len(result.errors) - 10} more errors")

    print("=" * 80)


async def main():
    """Main entry point."""
    args = parse_arguments()

    print("=" * 80)
    print("DOCUMENT INGESTION TOOL")
    print("=" * 80)
    print(f"Collection: {args.collection}")
    print(f"Chunk Strategy: {args.chunk_strategy}")
    print(f"Batch Size: {args.batch_size}")
    if args.use_mock_embeddings:
        print("Embeddings: MOCK (testing mode)")
    else:
        print("Embeddings: API (requires valid key)")
    print("=" * 80)

    if args.init_collections:
        print("\nInitializing Qdrant collections...")
        QdrantManager.initialize_collections()
        print("Collections initialized.")

    additional_metadata = parse_metadata(args.metadata)

    pipeline = IngestionPipeline(
        chunk_strategy=args.chunk_strategy,
        collection_name=args.collection,
        use_mock_embeddings=args.use_mock_embeddings,
    )

    result: IngestionResult = None

    try:
        if args.input_files:
            file_paths = [fp.strip() for fp in args.input_files.split(",")]

            if len(file_paths) == 1:
                single_result = await ingest_single_file(
                    file_path=file_paths[0],
                    pipeline=pipeline,
                    verbose=args.verbose,
                )

                if single_result.get("success"):
                    result = IngestionResult(
                        total_documents=1,
                        successful=1,
                        failed=0,
                        total_chunks=single_result.get("chunks_processed", 0),
                    )
                else:
                    result = IngestionResult(
                        total_documents=1,
                        successful=0,
                        failed=1,
                        total_chunks=0,
                        errors=[single_result.get("error", "Unknown error")],
                    )
            else:
                result = await ingest_files(
                    file_paths=file_paths,
                    pipeline=pipeline,
                    batch_size=args.batch_size,
                    verbose=args.verbose,
                )

        elif args.input_dir:
            file_extensions: Optional[list[str]] = None
            if args.file_extensions:
                file_extensions = [ext.strip() for ext in args.file_extensions.split(",")]

            result = await ingest_directory(
                directory_path=args.input_dir,
                pipeline=pipeline,
                recursive=args.recursive,
                batch_size=args.batch_size,
                file_extensions=file_extensions,
                verbose=args.verbose,
            )

        if result:
            print_summary(result)

            if result.successful > 0:
                print("\n✅ Ingestion completed successfully!")
            else:
                print("\n❌ Ingestion completed with errors.")
                sys.exit(1)
        else:
            print("\n❌ No documents were processed.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Ingestion interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

```

# backend/tests/integration/__init__.py
```py

```

# backend/tests/__init__.py
```py

```

# backend/tests/conftest.py
```py
"""Test configuration and fixtures."""

```

# backend/tests/evaluation/__init__.py
```py

```

# backend/tests/unit/__init__.py
```py

```

# frontend/components.json
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "src/app/globals.css",
    "baseColor": "zinc",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}

```

# frontend/package-lock.json
```json
{
  "name": "singapore-smb-support-agent-frontend",
  "version": "0.1.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "singapore-smb-support-agent-frontend",
      "version": "0.1.0",
      "dependencies": {
        "@fontsource-variable/inter": "^5.2.8",
        "@fontsource/manrope": "^5.2.8",
        "@radix-ui/react-avatar": "^1.1.11",
        "@radix-ui/react-dialog": "^1.1.15",
        "@radix-ui/react-scroll-area": "^1.2.10",
        "@radix-ui/react-separator": "^1.1.8",
        "@radix-ui/react-slot": "^1.2.4",
        "@tanstack/react-query": "^5.90.14",
        "clsx": "^2.1.1",
        "date-fns": "^4.1.0",
        "lucide-react": "^0.562.0",
        "next": "^15.5.9",
        "react": "^18.3.1",
        "react-dom": "^18.3.1",
        "tailwind-merge": "^3.4.0",
        "tailwindcss-animate": "^1.0.7",
        "zustand": "^5.0.9"
      },
      "devDependencies": {
        "@types/node": "^25.0.3",
        "@types/react": "^19.2.7",
        "@types/react-dom": "^19.2.3",
        "@typescript-eslint/eslint-plugin": "^8.50.1",
        "@typescript-eslint/parser": "^8.50.1",
        "autoprefixer": "^10.4.23",
        "eslint": "^9.39.2",
        "eslint-config-next": "^16.1.1",
        "postcss": "^8.5.6",
        "tailwindcss": "^3.4.19",
        "typescript": "^5.9.3"
      },
      "engines": {
        "node": ">=20.0.0"
      }
    },
    "node_modules/@alloc/quick-lru": {
      "version": "5.2.0",
      "resolved": "https://registry.npmjs.org/@alloc/quick-lru/-/quick-lru-5.2.0.tgz",
      "integrity": "sha512-UrcABB+4bUrFABwbluTIBErXwvbsU/V7TZWfmbgJfbkwiBuziS9gxdODUyuiecfdGQ85jglMW6juS3+z5TsKLw==",
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/@babel/code-frame": {
      "version": "7.27.1",
      "resolved": "https://registry.npmjs.org/@babel/code-frame/-/code-frame-7.27.1.tgz",
      "integrity": "sha512-cjQ7ZlQ0Mv3b47hABuTevyTuYN4i+loJKGeV9flcCgIK37cCXRh+L1bd3iBHlynerhQ7BhCkn2BPbQUL+rGqFg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-validator-identifier": "^7.27.1",
        "js-tokens": "^4.0.0",
        "picocolors": "^1.1.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/compat-data": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/compat-data/-/compat-data-7.28.5.tgz",
      "integrity": "sha512-6uFXyCayocRbqhZOB+6XcuZbkMNimwfVGFji8CTZnCzOHVGvDqzvitu1re2AU5LROliz7eQPhB8CpAMvnx9EjA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/core": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/core/-/core-7.28.5.tgz",
      "integrity": "sha512-e7jT4DxYvIDLk1ZHmU/m/mB19rex9sv0c2ftBtjSBv+kVM/902eh0fINUzD7UwLLNR+jU585GxUJ8/EBfAM5fw==",
      "dev": true,
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "@babel/code-frame": "^7.27.1",
        "@babel/generator": "^7.28.5",
        "@babel/helper-compilation-targets": "^7.27.2",
        "@babel/helper-module-transforms": "^7.28.3",
        "@babel/helpers": "^7.28.4",
        "@babel/parser": "^7.28.5",
        "@babel/template": "^7.27.2",
        "@babel/traverse": "^7.28.5",
        "@babel/types": "^7.28.5",
        "@jridgewell/remapping": "^2.3.5",
        "convert-source-map": "^2.0.0",
        "debug": "^4.1.0",
        "gensync": "^1.0.0-beta.2",
        "json5": "^2.2.3",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/babel"
      }
    },
    "node_modules/@babel/core/node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/@babel/generator": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/generator/-/generator-7.28.5.tgz",
      "integrity": "sha512-3EwLFhZ38J4VyIP6WNtt2kUdW9dokXA9Cr4IVIFHuCpZ3H8/YFOl5JjZHisrn1fATPBmKKqXzDFvh9fUwHz6CQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/parser": "^7.28.5",
        "@babel/types": "^7.28.5",
        "@jridgewell/gen-mapping": "^0.3.12",
        "@jridgewell/trace-mapping": "^0.3.28",
        "jsesc": "^3.0.2"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-compilation-targets": {
      "version": "7.27.2",
      "resolved": "https://registry.npmjs.org/@babel/helper-compilation-targets/-/helper-compilation-targets-7.27.2.tgz",
      "integrity": "sha512-2+1thGUUWWjLTYTHZWK1n8Yga0ijBz1XAhUXcKy81rd5g6yh7hGqMp45v7cadSbEHc9G3OTv45SyneRN3ps4DQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/compat-data": "^7.27.2",
        "@babel/helper-validator-option": "^7.27.1",
        "browserslist": "^4.24.0",
        "lru-cache": "^5.1.1",
        "semver": "^6.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-compilation-targets/node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/@babel/helper-globals": {
      "version": "7.28.0",
      "resolved": "https://registry.npmjs.org/@babel/helper-globals/-/helper-globals-7.28.0.tgz",
      "integrity": "sha512-+W6cISkXFa1jXsDEdYA8HeevQT/FULhxzR99pxphltZcVaugps53THCeiWA8SguxxpSp3gKPiuYfSWopkLQ4hw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-imports": {
      "version": "7.27.1",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-imports/-/helper-module-imports-7.27.1.tgz",
      "integrity": "sha512-0gSFWUPNXNopqtIPQvlD5WgXYI5GY2kP2cCvoT8kczjbfcfuIljTbcWrulD1CIPIX2gt1wghbDy08yE1p+/r3w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/traverse": "^7.27.1",
        "@babel/types": "^7.27.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-module-transforms": {
      "version": "7.28.3",
      "resolved": "https://registry.npmjs.org/@babel/helper-module-transforms/-/helper-module-transforms-7.28.3.tgz",
      "integrity": "sha512-gytXUbs8k2sXS9PnQptz5o0QnpLL51SwASIORY6XaBKF88nsOT0Zw9szLqlSGQDP/4TljBAD5y98p2U1fqkdsw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-module-imports": "^7.27.1",
        "@babel/helper-validator-identifier": "^7.27.1",
        "@babel/traverse": "^7.28.3"
      },
      "engines": {
        "node": ">=6.9.0"
      },
      "peerDependencies": {
        "@babel/core": "^7.0.0"
      }
    },
    "node_modules/@babel/helper-string-parser": {
      "version": "7.27.1",
      "resolved": "https://registry.npmjs.org/@babel/helper-string-parser/-/helper-string-parser-7.27.1.tgz",
      "integrity": "sha512-qMlSxKbpRlAridDExk92nSobyDdpPijUq2DW6oDnUqd0iOGxmQjyqhMIihI9+zv4LPyZdRje2cavWPbCbWm3eA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-identifier": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-identifier/-/helper-validator-identifier-7.28.5.tgz",
      "integrity": "sha512-qSs4ifwzKJSV39ucNjsvc6WVHs6b7S03sOh2OcHF9UHfVPqWWALUsNUVzhSBiItjRZoLHx7nIarVjqKVusUZ1Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helper-validator-option": {
      "version": "7.27.1",
      "resolved": "https://registry.npmjs.org/@babel/helper-validator-option/-/helper-validator-option-7.27.1.tgz",
      "integrity": "sha512-YvjJow9FxbhFFKDSuFnVCe2WxXk1zWc22fFePVNEaWJEu8IrZVlda6N0uHwzZrUM1il7NC9Mlp4MaJYbYd9JSg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/helpers": {
      "version": "7.28.4",
      "resolved": "https://registry.npmjs.org/@babel/helpers/-/helpers-7.28.4.tgz",
      "integrity": "sha512-HFN59MmQXGHVyYadKLVumYsA9dBFun/ldYxipEjzA4196jpLZd8UjEEBLkbEkvfYreDqJhZxYAWFPtrfhNpj4w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/template": "^7.27.2",
        "@babel/types": "^7.28.4"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/parser": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/parser/-/parser-7.28.5.tgz",
      "integrity": "sha512-KKBU1VGYR7ORr3At5HAtUQ+TV3SzRCXmA/8OdDZiLDBIZxVyzXuztPjfLd3BV1PRAQGCMWWSHYhL0F8d5uHBDQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/types": "^7.28.5"
      },
      "bin": {
        "parser": "bin/babel-parser.js"
      },
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@babel/template": {
      "version": "7.27.2",
      "resolved": "https://registry.npmjs.org/@babel/template/-/template-7.27.2.tgz",
      "integrity": "sha512-LPDZ85aEJyYSd18/DkjNh4/y1ntkE5KwUHWTiqgRxruuZL2F1yuHligVHLvcHY2vMHXttKFpJn6LwfI7cw7ODw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.27.1",
        "@babel/parser": "^7.27.2",
        "@babel/types": "^7.27.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/traverse": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/traverse/-/traverse-7.28.5.tgz",
      "integrity": "sha512-TCCj4t55U90khlYkVV/0TfkJkAkUg3jZFA3Neb7unZT8CPok7iiRfaX0F+WnqWqt7OxhOn0uBKXCw4lbL8W0aQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/code-frame": "^7.27.1",
        "@babel/generator": "^7.28.5",
        "@babel/helper-globals": "^7.28.0",
        "@babel/parser": "^7.28.5",
        "@babel/template": "^7.27.2",
        "@babel/types": "^7.28.5",
        "debug": "^4.3.1"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@babel/types": {
      "version": "7.28.5",
      "resolved": "https://registry.npmjs.org/@babel/types/-/types-7.28.5.tgz",
      "integrity": "sha512-qQ5m48eI/MFLQ5PxQj4PFaprjyCTLI37ElWMmNs0K8Lk3dVeOdNpB3ks8jc7yM5CDmVC73eMVk/trk3fgmrUpA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/helper-string-parser": "^7.27.1",
        "@babel/helper-validator-identifier": "^7.28.5"
      },
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/@emnapi/core": {
      "version": "1.7.1",
      "resolved": "https://registry.npmjs.org/@emnapi/core/-/core-1.7.1.tgz",
      "integrity": "sha512-o1uhUASyo921r2XtHYOHy7gdkGLge8ghBEQHMWmyJFoXlpU58kIrhhN3w26lpQb6dspetweapMn2CSNwQ8I4wg==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/wasi-threads": "1.1.0",
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@emnapi/runtime": {
      "version": "1.7.1",
      "resolved": "https://registry.npmjs.org/@emnapi/runtime/-/runtime-1.7.1.tgz",
      "integrity": "sha512-PVtJr5CmLwYAU9PZDMITZoR5iAOShYREoR45EyyLrbntV50mdePTgUn4AmOw90Ifcj+x2kRjdzr1HP3RrNiHGA==",
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@emnapi/wasi-threads": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@emnapi/wasi-threads/-/wasi-threads-1.1.0.tgz",
      "integrity": "sha512-WI0DdZ8xFSbgMjR1sFsKABJ/C5OnRrjT06JXbZKexJGrDuPTzZdDYfFlsgcCXCyf+suG5QU2e/y1Wo2V/OapLQ==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@eslint-community/eslint-utils": {
      "version": "4.9.0",
      "resolved": "https://registry.npmjs.org/@eslint-community/eslint-utils/-/eslint-utils-4.9.0.tgz",
      "integrity": "sha512-ayVFHdtZ+hsq1t2Dy24wCmGXGe4q9Gu3smhLYALJrr473ZH27MsnSL+LKUlimp4BWJqMDMLmPpx/Q9R3OAlL4g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "eslint-visitor-keys": "^3.4.3"
      },
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      },
      "peerDependencies": {
        "eslint": "^6.0.0 || ^7.0.0 || >=8.0.0"
      }
    },
    "node_modules/@eslint-community/regexpp": {
      "version": "4.12.2",
      "resolved": "https://registry.npmjs.org/@eslint-community/regexpp/-/regexpp-4.12.2.tgz",
      "integrity": "sha512-EriSTlt5OC9/7SXkRSCAhfSxxoSUgBm33OH+IkwbdpgoqsSsUg7y3uh+IICI/Qg4BBWr3U2i39RpmycbxMq4ew==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^12.0.0 || ^14.0.0 || >=16.0.0"
      }
    },
    "node_modules/@eslint/config-array": {
      "version": "0.21.1",
      "resolved": "https://registry.npmjs.org/@eslint/config-array/-/config-array-0.21.1.tgz",
      "integrity": "sha512-aw1gNayWpdI/jSYVgzN5pL0cfzU02GT3NBpeT/DXbx1/1x7ZKxFPd9bwrzygx/qiwIQiJ1sw/zD8qY/kRvlGHA==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/object-schema": "^2.1.7",
        "debug": "^4.3.1",
        "minimatch": "^3.1.2"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/config-array/node_modules/brace-expansion": {
      "version": "1.1.12",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.12.tgz",
      "integrity": "sha512-9T9UjW3r0UW5c1Q7GTwllptXwhvYmEzFhzMfZ9H7FQWt+uZePjZPjBP/W1ZEyZ1twGWom5/56TF4lPcqjnDHcg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/@eslint/config-array/node_modules/minimatch": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz",
      "integrity": "sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/@eslint/config-helpers": {
      "version": "0.4.2",
      "resolved": "https://registry.npmjs.org/@eslint/config-helpers/-/config-helpers-0.4.2.tgz",
      "integrity": "sha512-gBrxN88gOIf3R7ja5K9slwNayVcZgK6SOUORm2uBzTeIEfeVaIhOpCtTox3P6R7o2jLFwLFTLnC7kU/RGcYEgw==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/core": "^0.17.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/core": {
      "version": "0.17.0",
      "resolved": "https://registry.npmjs.org/@eslint/core/-/core-0.17.0.tgz",
      "integrity": "sha512-yL/sLrpmtDaFEiUj1osRP4TI2MDz1AddJL+jZ7KSqvBuliN4xqYY54IfdN8qD8Toa6g1iloph1fxQNkjOxrrpQ==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@types/json-schema": "^7.0.15"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/eslintrc": {
      "version": "3.3.3",
      "resolved": "https://registry.npmjs.org/@eslint/eslintrc/-/eslintrc-3.3.3.tgz",
      "integrity": "sha512-Kr+LPIUVKz2qkx1HAMH8q1q6azbqBAsXJUxBl/ODDuVPX45Z9DfwB8tPjTi6nNZ8BuM3nbJxC5zCAg5elnBUTQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ajv": "^6.12.4",
        "debug": "^4.3.2",
        "espree": "^10.0.1",
        "globals": "^14.0.0",
        "ignore": "^5.2.0",
        "import-fresh": "^3.2.1",
        "js-yaml": "^4.1.1",
        "minimatch": "^3.1.2",
        "strip-json-comments": "^3.1.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/@eslint/eslintrc/node_modules/brace-expansion": {
      "version": "1.1.12",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.12.tgz",
      "integrity": "sha512-9T9UjW3r0UW5c1Q7GTwllptXwhvYmEzFhzMfZ9H7FQWt+uZePjZPjBP/W1ZEyZ1twGWom5/56TF4lPcqjnDHcg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/@eslint/eslintrc/node_modules/ignore": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-5.3.2.tgz",
      "integrity": "sha512-hsBTNUqQTDwkWtcdYI2i06Y/nUBEsNEDJKjWdigLvegy8kDuJAS8uRlpkkcQpyEXL0Z/pjDy5HBmMjRCJ2gq+g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/@eslint/eslintrc/node_modules/minimatch": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz",
      "integrity": "sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/@eslint/js": {
      "version": "9.39.2",
      "resolved": "https://registry.npmjs.org/@eslint/js/-/js-9.39.2.tgz",
      "integrity": "sha512-q1mjIoW1VX4IvSocvM/vbTiveKC4k9eLrajNEuSsmjymSDEbpGddtpfOoN7YGAqBK3NG+uqo8ia4PDTt8buCYA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://eslint.org/donate"
      }
    },
    "node_modules/@eslint/object-schema": {
      "version": "2.1.7",
      "resolved": "https://registry.npmjs.org/@eslint/object-schema/-/object-schema-2.1.7.tgz",
      "integrity": "sha512-VtAOaymWVfZcmZbp6E2mympDIHvyjXs/12LqWYjVw6qjrfF+VK+fyG33kChz3nnK+SU5/NeHOqrTEHS8sXO3OA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@eslint/plugin-kit": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/@eslint/plugin-kit/-/plugin-kit-0.4.1.tgz",
      "integrity": "sha512-43/qtrDUokr7LJqoF2c3+RInu/t4zfrpYdoSDfYyhg52rwLV6TnOvdG4fXm7IkSB3wErkcmJS9iEhjVtOSEjjA==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@eslint/core": "^0.17.0",
        "levn": "^0.4.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      }
    },
    "node_modules/@fontsource-variable/inter": {
      "version": "5.2.8",
      "resolved": "https://registry.npmjs.org/@fontsource-variable/inter/-/inter-5.2.8.tgz",
      "integrity": "sha512-kOfP2D+ykbcX/P3IFnokOhVRNoTozo5/JxhAIVYLpea/UBmCQ/YWPBfWIDuBImXX/15KH+eKh4xpEUyS2sQQGQ==",
      "license": "OFL-1.1",
      "funding": {
        "url": "https://github.com/sponsors/ayuhito"
      }
    },
    "node_modules/@fontsource/manrope": {
      "version": "5.2.8",
      "resolved": "https://registry.npmjs.org/@fontsource/manrope/-/manrope-5.2.8.tgz",
      "integrity": "sha512-gJHJmcuUk7qWcNCfcAri/DJQtXtBYqi9yKratr4jXhSo0I3xUtNNKI+igQIcw5c+m95g0vounk8ZnX/kb8o0TA==",
      "license": "OFL-1.1",
      "funding": {
        "url": "https://github.com/sponsors/ayuhito"
      }
    },
    "node_modules/@humanfs/core": {
      "version": "0.19.1",
      "resolved": "https://registry.npmjs.org/@humanfs/core/-/core-0.19.1.tgz",
      "integrity": "sha512-5DyQ4+1JEUzejeK1JGICcideyfUbGixgS9jNgex5nqkW+cY7WZhxBigmieN5Qnw9ZosSNVC9KQKyb+GUaGyKUA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanfs/node": {
      "version": "0.16.7",
      "resolved": "https://registry.npmjs.org/@humanfs/node/-/node-0.16.7.tgz",
      "integrity": "sha512-/zUx+yOsIrG4Y43Eh2peDeKCxlRt/gET6aHfaKpuq267qXdYDFViVHfMaLyygZOnl0kGWxFIgsBy8QFuTLUXEQ==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "@humanfs/core": "^0.19.1",
        "@humanwhocodes/retry": "^0.4.0"
      },
      "engines": {
        "node": ">=18.18.0"
      }
    },
    "node_modules/@humanwhocodes/module-importer": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/module-importer/-/module-importer-1.0.1.tgz",
      "integrity": "sha512-bxveV4V8v5Yb4ncFTT3rPSgZBOpCkjfK0y4oVVVJwIuDVBRMDXrPyXRL988i5ap9m9bnyEEjWfm5WkBmtffLfA==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=12.22"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/nzakas"
      }
    },
    "node_modules/@humanwhocodes/retry": {
      "version": "0.4.3",
      "resolved": "https://registry.npmjs.org/@humanwhocodes/retry/-/retry-0.4.3.tgz",
      "integrity": "sha512-bV0Tgo9K4hfPCek+aMAn81RppFKv2ySDQeMoSZuvTASywNTnVJCArCZE2FWqpvIatKu7VMRLWlR1EazvVhDyhQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">=18.18"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/nzakas"
      }
    },
    "node_modules/@img/colour": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/@img/colour/-/colour-1.0.0.tgz",
      "integrity": "sha512-A5P/LfWGFSl6nsckYtjw9da+19jB8hkJ6ACTGcDfEJ0aE+l2n2El7dsVM7UVHZQ9s2lmYMWlrS21YLy2IR1LUw==",
      "license": "MIT",
      "optional": true,
      "engines": {
        "node": ">=18"
      }
    },
    "node_modules/@img/sharp-darwin-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-darwin-arm64/-/sharp-darwin-arm64-0.34.5.tgz",
      "integrity": "sha512-imtQ3WMJXbMY4fxb/Ndp6HBTNVtWCUI0WdobyheGf5+ad6xX8VIDO8u2xE4qc/fr08CKG/7dDseFtn6M6g/r3w==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-darwin-arm64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-darwin-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-darwin-x64/-/sharp-darwin-x64-0.34.5.tgz",
      "integrity": "sha512-YNEFAF/4KQ/PeW0N+r+aVVsoIY0/qxxikF2SWdp+NRkmMB7y9LBZAVqQ4yhGCm/H3H270OSykqmQMKLBhBJDEw==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-darwin-x64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-libvips-darwin-arm64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-darwin-arm64/-/sharp-libvips-darwin-arm64-1.2.4.tgz",
      "integrity": "sha512-zqjjo7RatFfFoP0MkQ51jfuFZBnVE2pRiaydKJ1G/rHZvnsrHAOcQALIi9sA5co5xenQdTugCvtb1cuf78Vf4g==",
      "cpu": [
        "arm64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "darwin"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-darwin-x64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-darwin-x64/-/sharp-libvips-darwin-x64-1.2.4.tgz",
      "integrity": "sha512-1IOd5xfVhlGwX+zXv2N93k0yMONvUlANylbJw1eTah8K/Jtpi15KC+WSiaX/nBmbm2HxRM1gZ0nSdjSsrZbGKg==",
      "cpu": [
        "x64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "darwin"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-arm": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-arm/-/sharp-libvips-linux-arm-1.2.4.tgz",
      "integrity": "sha512-bFI7xcKFELdiNCVov8e44Ia4u2byA+l3XtsAj+Q8tfCwO6BQ8iDojYdvoPMqsKDkuoOo+X6HZA0s0q11ANMQ8A==",
      "cpu": [
        "arm"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-arm64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-arm64/-/sharp-libvips-linux-arm64-1.2.4.tgz",
      "integrity": "sha512-excjX8DfsIcJ10x1Kzr4RcWe1edC9PquDRRPx3YVCvQv+U5p7Yin2s32ftzikXojb1PIFc/9Mt28/y+iRklkrw==",
      "cpu": [
        "arm64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-ppc64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-ppc64/-/sharp-libvips-linux-ppc64-1.2.4.tgz",
      "integrity": "sha512-FMuvGijLDYG6lW+b/UvyilUWu5Ayu+3r2d1S8notiGCIyYU/76eig1UfMmkZ7vwgOrzKzlQbFSuQfgm7GYUPpA==",
      "cpu": [
        "ppc64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-riscv64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-riscv64/-/sharp-libvips-linux-riscv64-1.2.4.tgz",
      "integrity": "sha512-oVDbcR4zUC0ce82teubSm+x6ETixtKZBh/qbREIOcI3cULzDyb18Sr/Wcyx7NRQeQzOiHTNbZFF1UwPS2scyGA==",
      "cpu": [
        "riscv64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-s390x": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-s390x/-/sharp-libvips-linux-s390x-1.2.4.tgz",
      "integrity": "sha512-qmp9VrzgPgMoGZyPvrQHqk02uyjA0/QrTO26Tqk6l4ZV0MPWIW6LTkqOIov+J1yEu7MbFQaDpwdwJKhbJvuRxQ==",
      "cpu": [
        "s390x"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linux-x64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linux-x64/-/sharp-libvips-linux-x64-1.2.4.tgz",
      "integrity": "sha512-tJxiiLsmHc9Ax1bz3oaOYBURTXGIRDODBqhveVHonrHJ9/+k89qbLl0bcJns+e4t4rvaNBxaEZsFtSfAdquPrw==",
      "cpu": [
        "x64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linuxmusl-arm64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linuxmusl-arm64/-/sharp-libvips-linuxmusl-arm64-1.2.4.tgz",
      "integrity": "sha512-FVQHuwx1IIuNow9QAbYUzJ+En8KcVm9Lk5+uGUQJHaZmMECZmOlix9HnH7n1TRkXMS0pGxIJokIVB9SuqZGGXw==",
      "cpu": [
        "arm64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-libvips-linuxmusl-x64": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@img/sharp-libvips-linuxmusl-x64/-/sharp-libvips-linuxmusl-x64-1.2.4.tgz",
      "integrity": "sha512-+LpyBk7L44ZIXwz/VYfglaX/okxezESc6UxDSoyo2Ks6Jxc4Y7sGjpgU9s4PMgqgjj1gZCylTieNamqA1MF7Dg==",
      "cpu": [
        "x64"
      ],
      "license": "LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "linux"
      ],
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-linux-arm": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-arm/-/sharp-linux-arm-0.34.5.tgz",
      "integrity": "sha512-9dLqsvwtg1uuXBGZKsxem9595+ujv0sJ6Vi8wcTANSFpwV/GONat5eCkzQo/1O6zRIkh0m/8+5BjrRr7jDUSZw==",
      "cpu": [
        "arm"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-arm": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-arm64/-/sharp-linux-arm64-0.34.5.tgz",
      "integrity": "sha512-bKQzaJRY/bkPOXyKx5EVup7qkaojECG6NLYswgktOZjaXecSAeCWiZwwiFf3/Y+O1HrauiE3FVsGxFg8c24rZg==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-arm64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-ppc64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-ppc64/-/sharp-linux-ppc64-0.34.5.tgz",
      "integrity": "sha512-7zznwNaqW6YtsfrGGDA6BRkISKAAE1Jo0QdpNYXNMHu2+0dTrPflTLNkpc8l7MUP5M16ZJcUvysVWWrMefZquA==",
      "cpu": [
        "ppc64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-ppc64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-riscv64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-riscv64/-/sharp-linux-riscv64-0.34.5.tgz",
      "integrity": "sha512-51gJuLPTKa7piYPaVs8GmByo7/U7/7TZOq+cnXJIHZKavIRHAP77e3N2HEl3dgiqdD/w0yUfiJnII77PuDDFdw==",
      "cpu": [
        "riscv64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-riscv64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-s390x": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-s390x/-/sharp-linux-s390x-0.34.5.tgz",
      "integrity": "sha512-nQtCk0PdKfho3eC5MrbQoigJ2gd1CgddUMkabUj+rBevs8tZ2cULOx46E7oyX+04WGfABgIwmMC0VqieTiR4jg==",
      "cpu": [
        "s390x"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-s390x": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linux-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linux-x64/-/sharp-linux-x64-0.34.5.tgz",
      "integrity": "sha512-MEzd8HPKxVxVenwAa+JRPwEC7QFjoPWuS5NZnBt6B3pu7EG2Ge0id1oLHZpPJdn3OQK+BQDiw9zStiHBTJQQQQ==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linux-x64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linuxmusl-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linuxmusl-arm64/-/sharp-linuxmusl-arm64-0.34.5.tgz",
      "integrity": "sha512-fprJR6GtRsMt6Kyfq44IsChVZeGN97gTD331weR1ex1c1rypDEABN6Tm2xa1wE6lYb5DdEnk03NZPqA7Id21yg==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linuxmusl-arm64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-linuxmusl-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-linuxmusl-x64/-/sharp-linuxmusl-x64-0.34.5.tgz",
      "integrity": "sha512-Jg8wNT1MUzIvhBFxViqrEhWDGzqymo3sV7z7ZsaWbZNDLXRJZoRGrjulp60YYtV4wfY8VIKcWidjojlLcWrd8Q==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-libvips-linuxmusl-x64": "1.2.4"
      }
    },
    "node_modules/@img/sharp-wasm32": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-wasm32/-/sharp-wasm32-0.34.5.tgz",
      "integrity": "sha512-OdWTEiVkY2PHwqkbBI8frFxQQFekHaSSkUIJkwzclWZe64O1X4UlUjqqqLaPbUpMOQk6FBu/HtlGXNblIs0huw==",
      "cpu": [
        "wasm32"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later AND MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/runtime": "^1.7.0"
      },
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-win32-arm64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-win32-arm64/-/sharp-win32-arm64-0.34.5.tgz",
      "integrity": "sha512-WQ3AgWCWYSb2yt+IG8mnC6Jdk9Whs7O0gxphblsLvdhSpSTtmu69ZG1Gkb6NuvxsNACwiPV6cNSZNzt0KPsw7g==",
      "cpu": [
        "arm64"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-win32-ia32": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-win32-ia32/-/sharp-win32-ia32-0.34.5.tgz",
      "integrity": "sha512-FV9m/7NmeCmSHDD5j4+4pNI8Cp3aW+JvLoXcTUo0IqyjSfAZJ8dIUmijx1qaJsIiU+Hosw6xM5KijAWRJCSgNg==",
      "cpu": [
        "ia32"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@img/sharp-win32-x64": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/@img/sharp-win32-x64/-/sharp-win32-x64-0.34.5.tgz",
      "integrity": "sha512-+29YMsqY2/9eFEiW93eqWnuLcWcufowXewwSNIT6UwZdUUCrM3oFjMWH/Z6/TMmb4hlFenmfAVbpWeup2jryCw==",
      "cpu": [
        "x64"
      ],
      "license": "Apache-2.0 AND LGPL-3.0-or-later",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      }
    },
    "node_modules/@jridgewell/gen-mapping": {
      "version": "0.3.13",
      "resolved": "https://registry.npmjs.org/@jridgewell/gen-mapping/-/gen-mapping-0.3.13.tgz",
      "integrity": "sha512-2kkt/7niJ6MgEPxF0bYdQ6etZaA+fQvDcLKckhy1yIQOzaoKjBBjSj63/aLVjYE3qhRt5dvM+uUyfCg6UKCBbA==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/sourcemap-codec": "^1.5.0",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/remapping": {
      "version": "2.3.5",
      "resolved": "https://registry.npmjs.org/@jridgewell/remapping/-/remapping-2.3.5.tgz",
      "integrity": "sha512-LI9u/+laYG4Ds1TDKSJW2YPrIlcVYOwi2fUC6xB43lueCjgxV4lffOCZCtYFiH6TNOX+tQKXx97T4IKHbhyHEQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@jridgewell/gen-mapping": "^0.3.5",
        "@jridgewell/trace-mapping": "^0.3.24"
      }
    },
    "node_modules/@jridgewell/resolve-uri": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/@jridgewell/resolve-uri/-/resolve-uri-3.1.2.tgz",
      "integrity": "sha512-bRISgCIjP20/tbWSPWMEi54QVPRZExkuD9lJL+UIxUKtwVJA8wW1Trb1jMs1RFXo1CBTNZ/5hpC9QvmKWdopKw==",
      "license": "MIT",
      "engines": {
        "node": ">=6.0.0"
      }
    },
    "node_modules/@jridgewell/sourcemap-codec": {
      "version": "1.5.5",
      "resolved": "https://registry.npmjs.org/@jridgewell/sourcemap-codec/-/sourcemap-codec-1.5.5.tgz",
      "integrity": "sha512-cYQ9310grqxueWbl+WuIUIaiUaDcj7WOq5fVhEljNVgRfOUhY9fy2zTvfoqWsnebh8Sl70VScFbICvJnLKB0Og==",
      "license": "MIT"
    },
    "node_modules/@jridgewell/trace-mapping": {
      "version": "0.3.31",
      "resolved": "https://registry.npmjs.org/@jridgewell/trace-mapping/-/trace-mapping-0.3.31.tgz",
      "integrity": "sha512-zzNR+SdQSDJzc8joaeP8QQoCQr8NuYx2dIIytl1QeBEZHJ9uW6hebsrYgbz8hJwUQao3TWCMtmfV8Nu1twOLAw==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/resolve-uri": "^3.1.0",
        "@jridgewell/sourcemap-codec": "^1.4.14"
      }
    },
    "node_modules/@napi-rs/wasm-runtime": {
      "version": "0.2.12",
      "resolved": "https://registry.npmjs.org/@napi-rs/wasm-runtime/-/wasm-runtime-0.2.12.tgz",
      "integrity": "sha512-ZVWUcfwY4E/yPitQJl481FjFo3K22D6qF0DuFH6Y/nbnE11GY5uguDxZMGXPQ8WQ0128MXQD7TnfHyK4oWoIJQ==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@emnapi/core": "^1.4.3",
        "@emnapi/runtime": "^1.4.3",
        "@tybys/wasm-util": "^0.10.0"
      }
    },
    "node_modules/@next/env": {
      "version": "15.5.9",
      "resolved": "https://registry.npmjs.org/@next/env/-/env-15.5.9.tgz",
      "integrity": "sha512-4GlTZ+EJM7WaW2HEZcyU317tIQDjkQIyENDLxYJfSWlfqguN+dHkZgyQTV/7ykvobU7yEH5gKvreNrH4B6QgIg==",
      "license": "MIT"
    },
    "node_modules/@next/eslint-plugin-next": {
      "version": "16.1.1",
      "resolved": "https://registry.npmjs.org/@next/eslint-plugin-next/-/eslint-plugin-next-16.1.1.tgz",
      "integrity": "sha512-Ovb/6TuLKbE1UiPcg0p39Ke3puyTCIKN9hGbNItmpQsp+WX3qrjO3WaMVSi6JHr9X1NrmthqIguVHodMJbh/dw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fast-glob": "3.3.1"
      }
    },
    "node_modules/@next/swc-darwin-arm64": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-darwin-arm64/-/swc-darwin-arm64-15.5.7.tgz",
      "integrity": "sha512-IZwtxCEpI91HVU/rAUOOobWSZv4P2DeTtNaCdHqLcTJU4wdNXgAySvKa/qJCgR5m6KI8UsKDXtO2B31jcaw1Yw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-darwin-x64": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-darwin-x64/-/swc-darwin-x64-15.5.7.tgz",
      "integrity": "sha512-UP6CaDBcqaCBuiq/gfCEJw7sPEoX1aIjZHnBWN9v9qYHQdMKvCKcAVs4OX1vIjeE+tC5EIuwDTVIoXpUes29lg==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-arm64-gnu": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-arm64-gnu/-/swc-linux-arm64-gnu-15.5.7.tgz",
      "integrity": "sha512-NCslw3GrNIw7OgmRBxHtdWFQYhexoUCq+0oS2ccjyYLtcn1SzGzeM54jpTFonIMUjNbHmpKpziXnpxhSWLcmBA==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-arm64-musl": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-arm64-musl/-/swc-linux-arm64-musl-15.5.7.tgz",
      "integrity": "sha512-nfymt+SE5cvtTrG9u1wdoxBr9bVB7mtKTcj0ltRn6gkP/2Nu1zM5ei8rwP9qKQP0Y//umK+TtkKgNtfboBxRrw==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-x64-gnu": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-x64-gnu/-/swc-linux-x64-gnu-15.5.7.tgz",
      "integrity": "sha512-hvXcZvCaaEbCZcVzcY7E1uXN9xWZfFvkNHwbe/n4OkRhFWrs1J1QV+4U1BN06tXLdaS4DazEGXwgqnu/VMcmqw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-linux-x64-musl": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-linux-x64-musl/-/swc-linux-x64-musl-15.5.7.tgz",
      "integrity": "sha512-4IUO539b8FmF0odY6/SqANJdgwn1xs1GkPO5doZugwZ3ETF6JUdckk7RGmsfSf7ws8Qb2YB5It33mvNL/0acqA==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-win32-arm64-msvc": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-win32-arm64-msvc/-/swc-win32-arm64-msvc-15.5.7.tgz",
      "integrity": "sha512-CpJVTkYI3ZajQkC5vajM7/ApKJUOlm6uP4BknM3XKvJ7VXAvCqSjSLmM0LKdYzn6nBJVSjdclx8nYJSa3xlTgQ==",
      "cpu": [
        "arm64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@next/swc-win32-x64-msvc": {
      "version": "15.5.7",
      "resolved": "https://registry.npmjs.org/@next/swc-win32-x64-msvc/-/swc-win32-x64-msvc-15.5.7.tgz",
      "integrity": "sha512-gMzgBX164I6DN+9/PGA+9dQiwmTkE4TloBNx8Kv9UiGARsr9Nba7IpcBRA1iTV9vwlYnrE3Uy6I7Aj6qLjQuqw==",
      "cpu": [
        "x64"
      ],
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ],
      "engines": {
        "node": ">= 10"
      }
    },
    "node_modules/@nodelib/fs.scandir": {
      "version": "2.1.5",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.scandir/-/fs.scandir-2.1.5.tgz",
      "integrity": "sha512-vq24Bq3ym5HEQm2NKCr3yXDwjc7vTsEThRDnkp2DK9p1uqLR+DHurm/NOTo0KG7HYHU7eppKZj3MyqYuMBf62g==",
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.stat": "2.0.5",
        "run-parallel": "^1.1.9"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nodelib/fs.stat": {
      "version": "2.0.5",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.stat/-/fs.stat-2.0.5.tgz",
      "integrity": "sha512-RkhPPp2zrqDAQA/2jNhnztcPAlv64XdhIp7a7454A5ovI7Bukxgt7MX7udwAu3zg1DcpPU0rz3VV1SeaqvY4+A==",
      "license": "MIT",
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nodelib/fs.walk": {
      "version": "1.2.8",
      "resolved": "https://registry.npmjs.org/@nodelib/fs.walk/-/fs.walk-1.2.8.tgz",
      "integrity": "sha512-oGB+UxlgWcgQkgwo8GcEGwemoTFt3FIO9ababBmaGwXIoBKZ+GTy0pP185beGg7Llih/NSHSV2XAs1lnznocSg==",
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.scandir": "2.1.5",
        "fastq": "^1.6.0"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/@nolyfill/is-core-module": {
      "version": "1.0.39",
      "resolved": "https://registry.npmjs.org/@nolyfill/is-core-module/-/is-core-module-1.0.39.tgz",
      "integrity": "sha512-nn5ozdjYQpUCZlWGuxcJY/KpxkWQs4DcbMCmKojjyrYDEAGy4Ce19NN4v5MduafTwJlbKc99UA8YhSVqq9yPZA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=12.4.0"
      }
    },
    "node_modules/@radix-ui/number": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/number/-/number-1.1.1.tgz",
      "integrity": "sha512-MkKCwxlXTgz6CFoJx3pCwn07GKp36+aZyu/u2Ln2VrA5DcdyCZkASEDBTd8x5whTQQL5CiYf4prXKLcgQdv29g==",
      "license": "MIT"
    },
    "node_modules/@radix-ui/primitive": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/primitive/-/primitive-1.1.3.tgz",
      "integrity": "sha512-JTF99U/6XIjCBo0wqkU5sK10glYe27MRRsfwoiq5zzOEZLHU3A3KCMa5X/azekYRCJ0HlwI0crAXS/5dEHTzDg==",
      "license": "MIT"
    },
    "node_modules/@radix-ui/react-avatar": {
      "version": "1.1.11",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-avatar/-/react-avatar-1.1.11.tgz",
      "integrity": "sha512-0Qk603AHGV28BOBO34p7IgD5m+V5Sg/YovfayABkoDDBM5d3NCx0Mp4gGrjzLGes1jV5eNOE1r3itqOR33VC6Q==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-context": "1.1.3",
        "@radix-ui/react-primitive": "2.1.4",
        "@radix-ui/react-use-callback-ref": "1.1.1",
        "@radix-ui/react-use-is-hydrated": "0.1.0",
        "@radix-ui/react-use-layout-effect": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-compose-refs": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-compose-refs/-/react-compose-refs-1.1.2.tgz",
      "integrity": "sha512-z4eqJvfiNnFMHIIvXP3CY57y2WJs5g2v3X0zm9mEJkrkNv4rDxu+sg9Jh8EkXyeqBkB7SOcboo9dMVqhyrACIg==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-context": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-context/-/react-context-1.1.3.tgz",
      "integrity": "sha512-ieIFACdMpYfMEjF0rEf5KLvfVyIkOz6PDGyNnP+u+4xQ6jny3VCgA4OgXOwNx2aUkxn8zx9fiVcM8CfFYv9Lxw==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dialog": {
      "version": "1.1.15",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-dialog/-/react-dialog-1.1.15.tgz",
      "integrity": "sha512-TCglVRtzlffRNxRMEyR36DGBLJpeusFcgMVD9PZEzAKnUs1lKCgX5u9BmC2Yg+LL9MgZDugFFs1Vl+Jp4t/PGw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.3",
        "@radix-ui/react-compose-refs": "1.1.2",
        "@radix-ui/react-context": "1.1.2",
        "@radix-ui/react-dismissable-layer": "1.1.11",
        "@radix-ui/react-focus-guards": "1.1.3",
        "@radix-ui/react-focus-scope": "1.1.7",
        "@radix-ui/react-id": "1.1.1",
        "@radix-ui/react-portal": "1.1.9",
        "@radix-ui/react-presence": "1.1.5",
        "@radix-ui/react-primitive": "2.1.3",
        "@radix-ui/react-slot": "1.2.3",
        "@radix-ui/react-use-controllable-state": "1.2.2",
        "aria-hidden": "^1.2.4",
        "react-remove-scroll": "^2.6.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dialog/node_modules/@radix-ui/react-context": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-context/-/react-context-1.1.2.tgz",
      "integrity": "sha512-jCi/QKUM2r1Ju5a3J64TH2A5SpKAgh0LpknyqdQ4m6DCV0xJ2HG1xARRwNGPQfi1SLdLWZ1OJz6F4OMBBNiGJA==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dialog/node_modules/@radix-ui/react-primitive": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-primitive/-/react-primitive-2.1.3.tgz",
      "integrity": "sha512-m9gTwRkhy2lvCPe6QJp4d3G1TYEUHn/FzJUtq9MjH46an1wJU+GdoGC5VLof8RX8Ft/DlpshApkhswDLZzHIcQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-slot": "1.2.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dialog/node_modules/@radix-ui/react-slot": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-slot/-/react-slot-1.2.3.tgz",
      "integrity": "sha512-aeNmHnBxbi2St0au6VBVC7JXFlhLlOnvIIlePNniyUNAClzmtAUEY8/pBiK3iHjufOlwA+c20/8jngo7xcrg8A==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-direction": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-direction/-/react-direction-1.1.1.tgz",
      "integrity": "sha512-1UEWRX6jnOA2y4H5WczZ44gOOjTEmlqv1uNW4GAJEO5+bauCBhv8snY65Iw5/VOS/ghKN9gr2KjnLKxrsvoMVw==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dismissable-layer": {
      "version": "1.1.11",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-dismissable-layer/-/react-dismissable-layer-1.1.11.tgz",
      "integrity": "sha512-Nqcp+t5cTB8BinFkZgXiMJniQH0PsUt2k51FUhbdfeKvc4ACcG2uQniY/8+h1Yv6Kza4Q7lD7PQV0z0oicE0Mg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/primitive": "1.1.3",
        "@radix-ui/react-compose-refs": "1.1.2",
        "@radix-ui/react-primitive": "2.1.3",
        "@radix-ui/react-use-callback-ref": "1.1.1",
        "@radix-ui/react-use-escape-keydown": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dismissable-layer/node_modules/@radix-ui/react-primitive": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-primitive/-/react-primitive-2.1.3.tgz",
      "integrity": "sha512-m9gTwRkhy2lvCPe6QJp4d3G1TYEUHn/FzJUtq9MjH46an1wJU+GdoGC5VLof8RX8Ft/DlpshApkhswDLZzHIcQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-slot": "1.2.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-dismissable-layer/node_modules/@radix-ui/react-slot": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-slot/-/react-slot-1.2.3.tgz",
      "integrity": "sha512-aeNmHnBxbi2St0au6VBVC7JXFlhLlOnvIIlePNniyUNAClzmtAUEY8/pBiK3iHjufOlwA+c20/8jngo7xcrg8A==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-focus-guards": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-focus-guards/-/react-focus-guards-1.1.3.tgz",
      "integrity": "sha512-0rFg/Rj2Q62NCm62jZw0QX7a3sz6QCQU0LpZdNrJX8byRGaGVTqbrW9jAoIAHyMQqsNpeZ81YgSizOt5WXq0Pw==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-focus-scope": {
      "version": "1.1.7",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-focus-scope/-/react-focus-scope-1.1.7.tgz",
      "integrity": "sha512-t2ODlkXBQyn7jkl6TNaw/MtVEVvIGelJDCG41Okq/KwUsJBwQ4XVZsHAVUkK4mBv3ewiAS3PGuUWuY2BoK4ZUw==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2",
        "@radix-ui/react-primitive": "2.1.3",
        "@radix-ui/react-use-callback-ref": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-focus-scope/node_modules/@radix-ui/react-primitive": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-primitive/-/react-primitive-2.1.3.tgz",
      "integrity": "sha512-m9gTwRkhy2lvCPe6QJp4d3G1TYEUHn/FzJUtq9MjH46an1wJU+GdoGC5VLof8RX8Ft/DlpshApkhswDLZzHIcQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-slot": "1.2.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-focus-scope/node_modules/@radix-ui/react-slot": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-slot/-/react-slot-1.2.3.tgz",
      "integrity": "sha512-aeNmHnBxbi2St0au6VBVC7JXFlhLlOnvIIlePNniyUNAClzmtAUEY8/pBiK3iHjufOlwA+c20/8jngo7xcrg8A==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-id": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-id/-/react-id-1.1.1.tgz",
      "integrity": "sha512-kGkGegYIdQsOb4XjsfM97rXsiHaBwco+hFI66oO4s9LU+PLAC5oJ7khdOVFxkhsmlbpUqDAvXw11CluXP+jkHg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-layout-effect": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-portal": {
      "version": "1.1.9",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-portal/-/react-portal-1.1.9.tgz",
      "integrity": "sha512-bpIxvq03if6UNwXZ+HTK71JLh4APvnXntDc6XOX8UVq4XQOVl7lwok0AvIl+b8zgCw3fSaVTZMpAPPagXbKmHQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-primitive": "2.1.3",
        "@radix-ui/react-use-layout-effect": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-portal/node_modules/@radix-ui/react-primitive": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-primitive/-/react-primitive-2.1.3.tgz",
      "integrity": "sha512-m9gTwRkhy2lvCPe6QJp4d3G1TYEUHn/FzJUtq9MjH46an1wJU+GdoGC5VLof8RX8Ft/DlpshApkhswDLZzHIcQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-slot": "1.2.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-portal/node_modules/@radix-ui/react-slot": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-slot/-/react-slot-1.2.3.tgz",
      "integrity": "sha512-aeNmHnBxbi2St0au6VBVC7JXFlhLlOnvIIlePNniyUNAClzmtAUEY8/pBiK3iHjufOlwA+c20/8jngo7xcrg8A==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-presence": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-presence/-/react-presence-1.1.5.tgz",
      "integrity": "sha512-/jfEwNDdQVBCNvjkGit4h6pMOzq8bHkopq458dPt2lMjx+eBQUohZNG9A7DtO/O5ukSbxuaNGXMjHicgwy6rQQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2",
        "@radix-ui/react-use-layout-effect": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-primitive": {
      "version": "2.1.4",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-primitive/-/react-primitive-2.1.4.tgz",
      "integrity": "sha512-9hQc4+GNVtJAIEPEqlYqW5RiYdrr8ea5XQ0ZOnD6fgru+83kqT15mq2OCcbe8KnjRZl5vF3ks69AKz3kh1jrhg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-slot": "1.2.4"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-scroll-area": {
      "version": "1.2.10",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-scroll-area/-/react-scroll-area-1.2.10.tgz",
      "integrity": "sha512-tAXIa1g3sM5CGpVT0uIbUx/U3Gs5N8T52IICuCtObaos1S8fzsrPXG5WObkQN3S6NVl6wKgPhAIiBGbWnvc97A==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/number": "1.1.1",
        "@radix-ui/primitive": "1.1.3",
        "@radix-ui/react-compose-refs": "1.1.2",
        "@radix-ui/react-context": "1.1.2",
        "@radix-ui/react-direction": "1.1.1",
        "@radix-ui/react-presence": "1.1.5",
        "@radix-ui/react-primitive": "2.1.3",
        "@radix-ui/react-use-callback-ref": "1.1.1",
        "@radix-ui/react-use-layout-effect": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-scroll-area/node_modules/@radix-ui/react-context": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-context/-/react-context-1.1.2.tgz",
      "integrity": "sha512-jCi/QKUM2r1Ju5a3J64TH2A5SpKAgh0LpknyqdQ4m6DCV0xJ2HG1xARRwNGPQfi1SLdLWZ1OJz6F4OMBBNiGJA==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-scroll-area/node_modules/@radix-ui/react-primitive": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-primitive/-/react-primitive-2.1.3.tgz",
      "integrity": "sha512-m9gTwRkhy2lvCPe6QJp4d3G1TYEUHn/FzJUtq9MjH46an1wJU+GdoGC5VLof8RX8Ft/DlpshApkhswDLZzHIcQ==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-slot": "1.2.3"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-scroll-area/node_modules/@radix-ui/react-slot": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-slot/-/react-slot-1.2.3.tgz",
      "integrity": "sha512-aeNmHnBxbi2St0au6VBVC7JXFlhLlOnvIIlePNniyUNAClzmtAUEY8/pBiK3iHjufOlwA+c20/8jngo7xcrg8A==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-separator": {
      "version": "1.1.8",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-separator/-/react-separator-1.1.8.tgz",
      "integrity": "sha512-sDvqVY4itsKwwSMEe0jtKgfTh+72Sy3gPmQpjqcQneqQ4PFmr/1I0YA+2/puilhggCe2gJcx5EBAYFkWkdpa5g==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-primitive": "2.1.4"
      },
      "peerDependencies": {
        "@types/react": "*",
        "@types/react-dom": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc",
        "react-dom": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "@types/react-dom": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-slot": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-slot/-/react-slot-1.2.4.tgz",
      "integrity": "sha512-Jl+bCv8HxKnlTLVrcDE8zTMJ09R9/ukw4qBs/oZClOfoQk/cOTbDn+NceXfV7j09YPVQUryJPHurafcSg6EVKA==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-compose-refs": "1.1.2"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-callback-ref": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-callback-ref/-/react-use-callback-ref-1.1.1.tgz",
      "integrity": "sha512-FkBMwD+qbGQeMu1cOHnuGB6x4yzPjho8ap5WtbEJ26umhgqVXbhekKUQO+hZEL1vU92a3wHwdp0HAcqAUF5iDg==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-controllable-state": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-controllable-state/-/react-use-controllable-state-1.2.2.tgz",
      "integrity": "sha512-BjasUjixPFdS+NKkypcyyN5Pmg83Olst0+c6vGov0diwTEo6mgdqVR6hxcEgFuh4QrAs7Rc+9KuGJ9TVCj0Zzg==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-effect-event": "0.0.2",
        "@radix-ui/react-use-layout-effect": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-effect-event": {
      "version": "0.0.2",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-effect-event/-/react-use-effect-event-0.0.2.tgz",
      "integrity": "sha512-Qp8WbZOBe+blgpuUT+lw2xheLP8q0oatc9UpmiemEICxGvFLYmHm9QowVZGHtJlGbS6A6yJ3iViad/2cVjnOiA==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-layout-effect": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-escape-keydown": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-escape-keydown/-/react-use-escape-keydown-1.1.1.tgz",
      "integrity": "sha512-Il0+boE7w/XebUHyBjroE+DbByORGR9KKmITzbR7MyQ4akpORYP/ZmbhAr0DG7RmmBqoOnZdy2QlvajJ2QA59g==",
      "license": "MIT",
      "dependencies": {
        "@radix-ui/react-use-callback-ref": "1.1.1"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-is-hydrated": {
      "version": "0.1.0",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-is-hydrated/-/react-use-is-hydrated-0.1.0.tgz",
      "integrity": "sha512-U+UORVEq+cTnRIaostJv9AGdV3G6Y+zbVd+12e18jQ5A3c0xL03IhnHuiU4UV69wolOQp5GfR58NW/EgdQhwOA==",
      "license": "MIT",
      "dependencies": {
        "use-sync-external-store": "^1.5.0"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@radix-ui/react-use-layout-effect": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/@radix-ui/react-use-layout-effect/-/react-use-layout-effect-1.1.1.tgz",
      "integrity": "sha512-RbJRS4UWQFkzHTTwVymMTUv8EqYhOp8dOOviLj2ugtTiXRaRQS7GLGxZTLL1jWhMeoSCf5zmcZkqTl9IiYfXcQ==",
      "license": "MIT",
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8 || ^17.0 || ^18.0 || ^19.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/@rtsao/scc": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/@rtsao/scc/-/scc-1.1.0.tgz",
      "integrity": "sha512-zt6OdqaDoOnJ1ZYsCYGt9YmWzDXl4vQdKTyJev62gFhRGKdx7mcT54V9KIjg+d2wi9EXsPvAPKe7i7WjfVWB8g==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@swc/helpers": {
      "version": "0.5.15",
      "resolved": "https://registry.npmjs.org/@swc/helpers/-/helpers-0.5.15.tgz",
      "integrity": "sha512-JQ5TuMi45Owi4/BIMAJBoSQoOJu12oOk/gADqlcUL9JEdHB8vyjUSsxqeNXnmXHjYKMi2WcYtezGEEhqUI/E2g==",
      "license": "Apache-2.0",
      "dependencies": {
        "tslib": "^2.8.0"
      }
    },
    "node_modules/@tanstack/query-core": {
      "version": "5.90.14",
      "resolved": "https://registry.npmjs.org/@tanstack/query-core/-/query-core-5.90.14.tgz",
      "integrity": "sha512-/6di2yNI+YxpVrH9Ig74Q+puKnkCE+D0LGyagJEGndJHJc6ahkcc/UqirHKy8zCYE/N9KLggxcQvzYCsUBWgdw==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/tannerlinsley"
      }
    },
    "node_modules/@tanstack/react-query": {
      "version": "5.90.14",
      "resolved": "https://registry.npmjs.org/@tanstack/react-query/-/react-query-5.90.14.tgz",
      "integrity": "sha512-JAMuULej09hrZ14W9+mxoRZ44rR2BuZfCd6oKTQVNfynQxCN3muH3jh3W46gqZNw5ZqY0ZVaS43Imb3dMr6tgw==",
      "license": "MIT",
      "dependencies": {
        "@tanstack/query-core": "5.90.14"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/tannerlinsley"
      },
      "peerDependencies": {
        "react": "^18 || ^19"
      }
    },
    "node_modules/@tybys/wasm-util": {
      "version": "0.10.1",
      "resolved": "https://registry.npmjs.org/@tybys/wasm-util/-/wasm-util-0.10.1.tgz",
      "integrity": "sha512-9tTaPJLSiejZKx+Bmog4uSubteqTvFrVrURwkmHixBo0G4seD0zUxp98E1DzUBJxLQ3NPwXrGKDiVjwx/DpPsg==",
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "tslib": "^2.4.0"
      }
    },
    "node_modules/@types/estree": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/@types/estree/-/estree-1.0.8.tgz",
      "integrity": "sha512-dWHzHa2WqEXI/O1E9OjrocMTKJl2mSrEolh1Iomrv6U+JuNwaHXsXx9bLu5gG7BUWFIN0skIQJQ/L1rIex4X6w==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/json-schema": {
      "version": "7.0.15",
      "resolved": "https://registry.npmjs.org/@types/json-schema/-/json-schema-7.0.15.tgz",
      "integrity": "sha512-5+fP8P8MFNC+AyZCDxrB2pkZFPGzqQWUzpSeuuVLvm8VMcorNYavBqoFcxK8bQz4Qsbn4oUEEem4wDLfcysGHA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/json5": {
      "version": "0.0.29",
      "resolved": "https://registry.npmjs.org/@types/json5/-/json5-0.0.29.tgz",
      "integrity": "sha512-dRLjCWHYg4oaA77cxO64oO+7JwCwnIzkZPdrrC71jQmQtlhM556pwKo5bUzqvZndkVbeFLIIi+9TC40JNF5hNQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/@types/node": {
      "version": "25.0.3",
      "resolved": "https://registry.npmjs.org/@types/node/-/node-25.0.3.tgz",
      "integrity": "sha512-W609buLVRVmeW693xKfzHeIV6nJGGz98uCPfeXI1ELMLXVeKYZ9m15fAMSaUPBHYLGFsVRcMmSCksQOrZV9BYA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "undici-types": "~7.16.0"
      }
    },
    "node_modules/@types/react": {
      "version": "19.2.7",
      "resolved": "https://registry.npmjs.org/@types/react/-/react-19.2.7.tgz",
      "integrity": "sha512-MWtvHrGZLFttgeEj28VXHxpmwYbor/ATPYbBfSFZEIRK0ecCFLl2Qo55z52Hss+UV9CRN7trSeq1zbgx7YDWWg==",
      "devOptional": true,
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "csstype": "^3.2.2"
      }
    },
    "node_modules/@types/react-dom": {
      "version": "19.2.3",
      "resolved": "https://registry.npmjs.org/@types/react-dom/-/react-dom-19.2.3.tgz",
      "integrity": "sha512-jp2L/eY6fn+KgVVQAOqYItbF0VY/YApe5Mz2F0aykSO8gx31bYCZyvSeYxCHKvzHG5eZjc+zyaS5BrBWya2+kQ==",
      "devOptional": true,
      "license": "MIT",
      "peer": true,
      "peerDependencies": {
        "@types/react": "^19.2.0"
      }
    },
    "node_modules/@typescript-eslint/eslint-plugin": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/eslint-plugin/-/eslint-plugin-8.50.1.tgz",
      "integrity": "sha512-PKhLGDq3JAg0Jk/aK890knnqduuI/Qj+udH7wCf0217IGi4gt+acgCyPVe79qoT+qKUvHMDQkwJeKW9fwl8Cyw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@eslint-community/regexpp": "^4.10.0",
        "@typescript-eslint/scope-manager": "8.50.1",
        "@typescript-eslint/type-utils": "8.50.1",
        "@typescript-eslint/utils": "8.50.1",
        "@typescript-eslint/visitor-keys": "8.50.1",
        "ignore": "^7.0.0",
        "natural-compare": "^1.4.0",
        "ts-api-utils": "^2.1.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "@typescript-eslint/parser": "^8.50.1",
        "eslint": "^8.57.0 || ^9.0.0",
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/@typescript-eslint/parser": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/parser/-/parser-8.50.1.tgz",
      "integrity": "sha512-hM5faZwg7aVNa819m/5r7D0h0c9yC4DUlWAOvHAtISdFTc8xB86VmX5Xqabrama3wIPJ/q9RbGS1worb6JfnMg==",
      "dev": true,
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "@typescript-eslint/scope-manager": "8.50.1",
        "@typescript-eslint/types": "8.50.1",
        "@typescript-eslint/typescript-estree": "8.50.1",
        "@typescript-eslint/visitor-keys": "8.50.1",
        "debug": "^4.3.4"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0",
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/@typescript-eslint/project-service": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/project-service/-/project-service-8.50.1.tgz",
      "integrity": "sha512-E1ur1MCVf+YiP89+o4Les/oBAVzmSbeRB0MQLfSlYtbWU17HPxZ6Bhs5iYmKZRALvEuBoXIZMOIRRc/P++Ortg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/tsconfig-utils": "^8.50.1",
        "@typescript-eslint/types": "^8.50.1",
        "debug": "^4.3.4"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/@typescript-eslint/scope-manager": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/scope-manager/-/scope-manager-8.50.1.tgz",
      "integrity": "sha512-mfRx06Myt3T4vuoHaKi8ZWNTPdzKPNBhiblze5N50//TSHOAQQevl/aolqA/BcqqbJ88GUnLqjjcBc8EWdBcVw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "8.50.1",
        "@typescript-eslint/visitor-keys": "8.50.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/tsconfig-utils": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/tsconfig-utils/-/tsconfig-utils-8.50.1.tgz",
      "integrity": "sha512-ooHmotT/lCWLXi55G4mvaUF60aJa012QzvLK0Y+Mp4WdSt17QhMhWOaBWeGTFVkb2gDgBe19Cxy1elPXylslDw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/@typescript-eslint/type-utils": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/type-utils/-/type-utils-8.50.1.tgz",
      "integrity": "sha512-7J3bf022QZE42tYMO6SL+6lTPKFk/WphhRPe9Tw/el+cEwzLz1Jjz2PX3GtGQVxooLDKeMVmMt7fWpYRdG5Etg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "8.50.1",
        "@typescript-eslint/typescript-estree": "8.50.1",
        "@typescript-eslint/utils": "8.50.1",
        "debug": "^4.3.4",
        "ts-api-utils": "^2.1.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0",
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/@typescript-eslint/types": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/types/-/types-8.50.1.tgz",
      "integrity": "sha512-v5lFIS2feTkNyMhd7AucE/9j/4V9v5iIbpVRncjk/K0sQ6Sb+Np9fgYS/63n6nwqahHQvbmujeBL7mp07Q9mlA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/typescript-estree": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/typescript-estree/-/typescript-estree-8.50.1.tgz",
      "integrity": "sha512-woHPdW+0gj53aM+cxchymJCrh0cyS7BTIdcDxWUNsclr9VDkOSbqC13juHzxOmQ22dDkMZEpZB+3X1WpUvzgVQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/project-service": "8.50.1",
        "@typescript-eslint/tsconfig-utils": "8.50.1",
        "@typescript-eslint/types": "8.50.1",
        "@typescript-eslint/visitor-keys": "8.50.1",
        "debug": "^4.3.4",
        "minimatch": "^9.0.4",
        "semver": "^7.6.0",
        "tinyglobby": "^0.2.15",
        "ts-api-utils": "^2.1.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/@typescript-eslint/utils": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/utils/-/utils-8.50.1.tgz",
      "integrity": "sha512-lCLp8H1T9T7gPbEuJSnHwnSuO9mDf8mfK/Nion5mZmiEaQD9sWf9W4dfeFqRyqRjF06/kBuTmAqcs9sewM2NbQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@eslint-community/eslint-utils": "^4.7.0",
        "@typescript-eslint/scope-manager": "8.50.1",
        "@typescript-eslint/types": "8.50.1",
        "@typescript-eslint/typescript-estree": "8.50.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0",
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/@typescript-eslint/visitor-keys": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/@typescript-eslint/visitor-keys/-/visitor-keys-8.50.1.tgz",
      "integrity": "sha512-IrDKrw7pCRUR94zeuCSUWQ+w8JEf5ZX5jl/e6AHGSLi1/zIr0lgutfn/7JpfCey+urpgQEdrZVYzCaVVKiTwhQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/types": "8.50.1",
        "eslint-visitor-keys": "^4.2.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      }
    },
    "node_modules/@typescript-eslint/visitor-keys/node_modules/eslint-visitor-keys": {
      "version": "4.2.1",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-4.2.1.tgz",
      "integrity": "sha512-Uhdk5sfqcee/9H/rCOJikYz67o0a2Tw2hGRPOG2Y1R2dg7brRe1uG0yaNQDHu+TO/uQPF/5eCapvYSmHUjt7JQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/@unrs/resolver-binding-android-arm-eabi": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-android-arm-eabi/-/resolver-binding-android-arm-eabi-1.11.1.tgz",
      "integrity": "sha512-ppLRUgHVaGRWUx0R0Ut06Mjo9gBaBkg3v/8AxusGLhsIotbBLuRk51rAzqLC8gq6NyyAojEXglNjzf6R948DNw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ]
    },
    "node_modules/@unrs/resolver-binding-android-arm64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-android-arm64/-/resolver-binding-android-arm64-1.11.1.tgz",
      "integrity": "sha512-lCxkVtb4wp1v+EoN+HjIG9cIIzPkX5OtM03pQYkG+U5O/wL53LC4QbIeazgiKqluGeVEeBlZahHalCaBvU1a2g==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "android"
      ]
    },
    "node_modules/@unrs/resolver-binding-darwin-arm64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-darwin-arm64/-/resolver-binding-darwin-arm64-1.11.1.tgz",
      "integrity": "sha512-gPVA1UjRu1Y/IsB/dQEsp2V1pm44Of6+LWvbLc9SDk1c2KhhDRDBUkQCYVWe6f26uJb3fOK8saWMgtX8IrMk3g==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ]
    },
    "node_modules/@unrs/resolver-binding-darwin-x64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-darwin-x64/-/resolver-binding-darwin-x64-1.11.1.tgz",
      "integrity": "sha512-cFzP7rWKd3lZaCsDze07QX1SC24lO8mPty9vdP+YVa3MGdVgPmFc59317b2ioXtgCMKGiCLxJ4HQs62oz6GfRQ==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ]
    },
    "node_modules/@unrs/resolver-binding-freebsd-x64": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-freebsd-x64/-/resolver-binding-freebsd-x64-1.11.1.tgz",
      "integrity": "sha512-fqtGgak3zX4DCB6PFpsH5+Kmt/8CIi4Bry4rb1ho6Av2QHTREM+47y282Uqiu3ZRF5IQioJQ5qWRV6jduA+iGw==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "freebsd"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm-gnueabihf": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm-gnueabihf/-/resolver-binding-linux-arm-gnueabihf-1.11.1.tgz",
      "integrity": "sha512-u92mvlcYtp9MRKmP+ZvMmtPN34+/3lMHlyMj7wXJDeXxuM0Vgzz0+PPJNsro1m3IZPYChIkn944wW8TYgGKFHw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm-musleabihf": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm-musleabihf/-/resolver-binding-linux-arm-musleabihf-1.11.1.tgz",
      "integrity": "sha512-cINaoY2z7LVCrfHkIcmvj7osTOtm6VVT16b5oQdS4beibX2SYBwgYLmqhBjA1t51CarSaBuX5YNsWLjsqfW5Cw==",
      "cpu": [
        "arm"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm64-gnu/-/resolver-binding-linux-arm64-gnu-1.11.1.tgz",
      "integrity": "sha512-34gw7PjDGB9JgePJEmhEqBhWvCiiWCuXsL9hYphDF7crW7UgI05gyBAi6MF58uGcMOiOqSJ2ybEeCvHcq0BCmQ==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-arm64-musl": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-arm64-musl/-/resolver-binding-linux-arm64-musl-1.11.1.tgz",
      "integrity": "sha512-RyMIx6Uf53hhOtJDIamSbTskA99sPHS96wxVE/bJtePJJtpdKGXO1wY90oRdXuYOGOTuqjT8ACccMc4K6QmT3w==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-ppc64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-ppc64-gnu/-/resolver-binding-linux-ppc64-gnu-1.11.1.tgz",
      "integrity": "sha512-D8Vae74A4/a+mZH0FbOkFJL9DSK2R6TFPC9M+jCWYia/q2einCubX10pecpDiTmkJVUH+y8K3BZClycD8nCShA==",
      "cpu": [
        "ppc64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-riscv64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-riscv64-gnu/-/resolver-binding-linux-riscv64-gnu-1.11.1.tgz",
      "integrity": "sha512-frxL4OrzOWVVsOc96+V3aqTIQl1O2TjgExV4EKgRY09AJ9leZpEg8Ak9phadbuX0BA4k8U5qtvMSQQGGmaJqcQ==",
      "cpu": [
        "riscv64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-riscv64-musl": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-riscv64-musl/-/resolver-binding-linux-riscv64-musl-1.11.1.tgz",
      "integrity": "sha512-mJ5vuDaIZ+l/acv01sHoXfpnyrNKOk/3aDoEdLO/Xtn9HuZlDD6jKxHlkN8ZhWyLJsRBxfv9GYM2utQ1SChKew==",
      "cpu": [
        "riscv64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-s390x-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-s390x-gnu/-/resolver-binding-linux-s390x-gnu-1.11.1.tgz",
      "integrity": "sha512-kELo8ebBVtb9sA7rMe1Cph4QHreByhaZ2QEADd9NzIQsYNQpt9UkM9iqr2lhGr5afh885d/cB5QeTXSbZHTYPg==",
      "cpu": [
        "s390x"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-x64-gnu": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-x64-gnu/-/resolver-binding-linux-x64-gnu-1.11.1.tgz",
      "integrity": "sha512-C3ZAHugKgovV5YvAMsxhq0gtXuwESUKc5MhEtjBpLoHPLYM+iuwSj3lflFwK3DPm68660rZ7G8BMcwSro7hD5w==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-linux-x64-musl": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-linux-x64-musl/-/resolver-binding-linux-x64-musl-1.11.1.tgz",
      "integrity": "sha512-rV0YSoyhK2nZ4vEswT/QwqzqQXw5I6CjoaYMOX0TqBlWhojUf8P94mvI7nuJTeaCkkds3QE4+zS8Ko+GdXuZtA==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "linux"
      ]
    },
    "node_modules/@unrs/resolver-binding-wasm32-wasi": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-wasm32-wasi/-/resolver-binding-wasm32-wasi-1.11.1.tgz",
      "integrity": "sha512-5u4RkfxJm+Ng7IWgkzi3qrFOvLvQYnPBmjmZQ8+szTK/b31fQCnleNl1GgEt7nIsZRIf5PLhPwT0WM+q45x/UQ==",
      "cpu": [
        "wasm32"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "dependencies": {
        "@napi-rs/wasm-runtime": "^0.2.11"
      },
      "engines": {
        "node": ">=14.0.0"
      }
    },
    "node_modules/@unrs/resolver-binding-win32-arm64-msvc": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-win32-arm64-msvc/-/resolver-binding-win32-arm64-msvc-1.11.1.tgz",
      "integrity": "sha512-nRcz5Il4ln0kMhfL8S3hLkxI85BXs3o8EYoattsJNdsX4YUU89iOkVn7g0VHSRxFuVMdM4Q1jEpIId1Ihim/Uw==",
      "cpu": [
        "arm64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/@unrs/resolver-binding-win32-ia32-msvc": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-win32-ia32-msvc/-/resolver-binding-win32-ia32-msvc-1.11.1.tgz",
      "integrity": "sha512-DCEI6t5i1NmAZp6pFonpD5m7i6aFrpofcp4LA2i8IIq60Jyo28hamKBxNrZcyOwVOZkgsRp9O2sXWBWP8MnvIQ==",
      "cpu": [
        "ia32"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/@unrs/resolver-binding-win32-x64-msvc": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/@unrs/resolver-binding-win32-x64-msvc/-/resolver-binding-win32-x64-msvc-1.11.1.tgz",
      "integrity": "sha512-lrW200hZdbfRtztbygyaq/6jP6AKE8qQN2KvPcJ+x7wiD038YtnYtZ82IMNJ69GJibV7bwL3y9FgK+5w/pYt6g==",
      "cpu": [
        "x64"
      ],
      "dev": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "win32"
      ]
    },
    "node_modules/acorn": {
      "version": "8.15.0",
      "resolved": "https://registry.npmjs.org/acorn/-/acorn-8.15.0.tgz",
      "integrity": "sha512-NZyJarBfL7nWwIq+FDL6Zp/yHEhePMNnnJ0y3qfieCrmNvYct8uvtiV41UvlSe6apAfk0fY1FbWx+NwfmpvtTg==",
      "dev": true,
      "license": "MIT",
      "peer": true,
      "bin": {
        "acorn": "bin/acorn"
      },
      "engines": {
        "node": ">=0.4.0"
      }
    },
    "node_modules/acorn-jsx": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/acorn-jsx/-/acorn-jsx-5.3.2.tgz",
      "integrity": "sha512-rq9s+JNhf0IChjtDXxllJ7g41oZk5SlXtp0LHwyA5cejwn7vKmKp4pPri6YEePv2PU65sAsegbXtIinmDFDXgQ==",
      "dev": true,
      "license": "MIT",
      "peerDependencies": {
        "acorn": "^6.0.0 || ^7.0.0 || ^8.0.0"
      }
    },
    "node_modules/ajv": {
      "version": "6.12.6",
      "resolved": "https://registry.npmjs.org/ajv/-/ajv-6.12.6.tgz",
      "integrity": "sha512-j3fVLgvTo527anyYyJOGTYJbG+vnnQYvE0m5mmkc1TK+nxAppkCLMIL0aZ4dblVCNoGShhm+kzE4ZUykBoMg4g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "fast-deep-equal": "^3.1.1",
        "fast-json-stable-stringify": "^2.0.0",
        "json-schema-traverse": "^0.4.1",
        "uri-js": "^4.2.2"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/epoberezkin"
      }
    },
    "node_modules/ansi-styles": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-4.3.0.tgz",
      "integrity": "sha512-zbB9rCJAT1rbjiVDb2hqKFHNYLxgtk8NURxZ3IZwD3F6NtxbXZQCnnSi1Lkx+IDohdPlFp222wVALIheZJQSEg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "color-convert": "^2.0.1"
      },
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/chalk/ansi-styles?sponsor=1"
      }
    },
    "node_modules/any-promise": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/any-promise/-/any-promise-1.3.0.tgz",
      "integrity": "sha512-7UvmKalWRt1wgjL1RrGxoSJW/0QZFIegpeGvZG9kjp8vrRu55XTHbwnqq2GpXm9uLbcuhxm3IqX9OB4MZR1b2A==",
      "license": "MIT"
    },
    "node_modules/anymatch": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/anymatch/-/anymatch-3.1.3.tgz",
      "integrity": "sha512-KMReFUr0B4t+D+OBkjR3KYqvocp2XaSzO55UcB6mgQMd3KbcE+mWTyvVV7D/zsdEbNnV6acZUutkiHQXvTr1Rw==",
      "license": "ISC",
      "dependencies": {
        "normalize-path": "^3.0.0",
        "picomatch": "^2.0.4"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/arg": {
      "version": "5.0.2",
      "resolved": "https://registry.npmjs.org/arg/-/arg-5.0.2.tgz",
      "integrity": "sha512-PYjyFOLKQ9y57JvQ6QLo8dAgNqswh8M1RMJYdQduT6xbWSgK36P/Z/v+p888pM69jMMfS8Xd8F6I1kQ/I9HUGg==",
      "license": "MIT"
    },
    "node_modules/argparse": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/argparse/-/argparse-2.0.1.tgz",
      "integrity": "sha512-8+9WqebbFzpX9OR+Wa6O29asIogeRMzcGtAINdpMHHyAg10f05aSFVBbcEqGf/PXw1EjAZ+q2/bEBg3DvurK3Q==",
      "dev": true,
      "license": "Python-2.0"
    },
    "node_modules/aria-hidden": {
      "version": "1.2.6",
      "resolved": "https://registry.npmjs.org/aria-hidden/-/aria-hidden-1.2.6.tgz",
      "integrity": "sha512-ik3ZgC9dY/lYVVM++OISsaYDeg1tb0VtP5uL3ouh1koGOaUMDPpbFIei4JkFimWUFPn90sbMNMXQAIVOlnYKJA==",
      "license": "MIT",
      "dependencies": {
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/aria-query": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/aria-query/-/aria-query-5.3.2.tgz",
      "integrity": "sha512-COROpnaoap1E2F000S62r6A60uHZnmlvomhfyT2DlTcrY1OrBKn2UhH7qn5wTC9zMvD0AY7csdPSNwKP+7WiQw==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/array-buffer-byte-length": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/array-buffer-byte-length/-/array-buffer-byte-length-1.0.2.tgz",
      "integrity": "sha512-LHE+8BuR7RYGDKvnrmcuSq3tDcKv9OFEXQt/HpbZhY7V6h0zlUXutnAD82GiFx9rdieCMjkvtcsPqBwgUl1Iiw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "is-array-buffer": "^3.0.5"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array-includes": {
      "version": "3.1.9",
      "resolved": "https://registry.npmjs.org/array-includes/-/array-includes-3.1.9.tgz",
      "integrity": "sha512-FmeCCAenzH0KH381SPT5FZmiA/TmpndpcaShhfgEN9eCVjnFBqq3l1xrI42y8+PPLI6hypzou4GXw00WHmPBLQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.24.0",
        "es-object-atoms": "^1.1.1",
        "get-intrinsic": "^1.3.0",
        "is-string": "^1.1.1",
        "math-intrinsics": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.findlast": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/array.prototype.findlast/-/array.prototype.findlast-1.2.5.tgz",
      "integrity": "sha512-CVvd6FHg1Z3POpBLxO6E6zr+rSKEQ9L6rZHAaY7lLfhKsWYUBBOuMs0e9o24oopj6H+geRCX0YJ+TJLBK2eHyQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.findlastindex": {
      "version": "1.2.6",
      "resolved": "https://registry.npmjs.org/array.prototype.findlastindex/-/array.prototype.findlastindex-1.2.6.tgz",
      "integrity": "sha512-F/TKATkzseUExPlfvmwQKGITM3DGTK+vkAsCZoDc5daVygbJBnjEUCbgkAvVFsgfXfX4YIqZ/27G3k3tdXrTxQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.9",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.1.1",
        "es-shim-unscopables": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.flat": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/array.prototype.flat/-/array.prototype.flat-1.3.3.tgz",
      "integrity": "sha512-rwG/ja1neyLqCuGZ5YYrznA62D4mZXg0i1cIskIUKSiqF3Cje9/wXAls9B9s1Wa2fomMsIv8czB8jZcPmxCXFg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.flatmap": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/array.prototype.flatmap/-/array.prototype.flatmap-1.3.3.tgz",
      "integrity": "sha512-Y7Wt51eKJSyi80hFrJCePGGNo5ktJCslFuboqJsbf57CCPcm5zztluPlc4/aD8sWsKvlwatezpV4U1efk8kpjg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/array.prototype.tosorted": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/array.prototype.tosorted/-/array.prototype.tosorted-1.1.4.tgz",
      "integrity": "sha512-p6Fx8B7b7ZhL/gmUsAy0D15WhvDccw3mnGNbZpi3pmeJdxtWsj2jEaI4Y6oo3XiHfzuSgPwKc04MYt6KgvC/wA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.3",
        "es-errors": "^1.3.0",
        "es-shim-unscopables": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/arraybuffer.prototype.slice": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/arraybuffer.prototype.slice/-/arraybuffer.prototype.slice-1.0.4.tgz",
      "integrity": "sha512-BNoCY6SXXPQ7gF2opIP4GBE+Xw7U+pHMYKuzjgCN3GwiaIR09UUeKfheyIry77QtrCBlC0KK0q5/TER/tYh3PQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-buffer-byte-length": "^1.0.1",
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6",
        "is-array-buffer": "^3.0.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/ast-types-flow": {
      "version": "0.0.8",
      "resolved": "https://registry.npmjs.org/ast-types-flow/-/ast-types-flow-0.0.8.tgz",
      "integrity": "sha512-OH/2E5Fg20h2aPrbe+QL8JZQFko0YZaF+j4mnQ7BGhfavO7OpSLa8a0y9sBwomHdSbkhTS8TQNayBfnW5DwbvQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/async-function": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/async-function/-/async-function-1.0.0.tgz",
      "integrity": "sha512-hsU18Ae8CDTR6Kgu9DYf0EbCr/a5iGL0rytQDobUcdpYOKokk8LEjVphnXkDkgpi0wYVsqrXuP0bZxJaTqdgoA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/autoprefixer": {
      "version": "10.4.23",
      "resolved": "https://registry.npmjs.org/autoprefixer/-/autoprefixer-10.4.23.tgz",
      "integrity": "sha512-YYTXSFulfwytnjAPlw8QHncHJmlvFKtczb8InXaAx9Q0LbfDnfEYDE55omerIJKihhmU61Ft+cAOSzQVaBUmeA==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/autoprefixer"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "browserslist": "^4.28.1",
        "caniuse-lite": "^1.0.30001760",
        "fraction.js": "^5.3.4",
        "picocolors": "^1.1.1",
        "postcss-value-parser": "^4.2.0"
      },
      "bin": {
        "autoprefixer": "bin/autoprefixer"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      },
      "peerDependencies": {
        "postcss": "^8.1.0"
      }
    },
    "node_modules/available-typed-arrays": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/available-typed-arrays/-/available-typed-arrays-1.0.7.tgz",
      "integrity": "sha512-wvUjBtSGN7+7SjNpq/9M2Tg350UZD3q62IFZLbRAR1bSMlCo1ZaeW+BJ+D090e4hIIZLBcTDWe4Mh4jvUDajzQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "possible-typed-array-names": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/axe-core": {
      "version": "4.11.0",
      "resolved": "https://registry.npmjs.org/axe-core/-/axe-core-4.11.0.tgz",
      "integrity": "sha512-ilYanEU8vxxBexpJd8cWM4ElSQq4QctCLKih0TSfjIfCQTeyH/6zVrmIJfLPrKTKJRbiG+cfnZbQIjAlJmF1jQ==",
      "dev": true,
      "license": "MPL-2.0",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/axobject-query": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/axobject-query/-/axobject-query-4.1.0.tgz",
      "integrity": "sha512-qIj0G9wZbMGNLjLmg1PT6v2mE9AH2zlnADJD/2tC6E00hgmhUOfEB6greHPAfLRSufHqROIUTkw6E+M3lH0PTQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/balanced-match": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/balanced-match/-/balanced-match-1.0.2.tgz",
      "integrity": "sha512-3oSeUO0TMV67hN1AmbXsK4yaqU7tjiHlbxRDZOpH0KW9+CeX4bRAaX0Anxt0tx2MrpRpWwQaPwIlISEJhYU5Pw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/baseline-browser-mapping": {
      "version": "2.9.11",
      "resolved": "https://registry.npmjs.org/baseline-browser-mapping/-/baseline-browser-mapping-2.9.11.tgz",
      "integrity": "sha512-Sg0xJUNDU1sJNGdfGWhVHX0kkZ+HWcvmVymJbj6NSgZZmW/8S9Y2HQ5euytnIgakgxN6papOAWiwDo1ctFDcoQ==",
      "dev": true,
      "license": "Apache-2.0",
      "bin": {
        "baseline-browser-mapping": "dist/cli.js"
      }
    },
    "node_modules/binary-extensions": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/binary-extensions/-/binary-extensions-2.3.0.tgz",
      "integrity": "sha512-Ceh+7ox5qe7LJuLHoY0feh3pHuUDHAcRUeyL2VYghZwfpkNIy/+8Ocg0a3UuSoYzavmylwuLWQOf3hl0jjMMIw==",
      "license": "MIT",
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/brace-expansion": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-2.0.2.tgz",
      "integrity": "sha512-Jt0vHyM+jmUBqojB7E1NIYadt0vI0Qxjxd2TErW94wDz+E2LAm5vKMXXwg6ZZBTHPuUlDgQHKXvjGBdfcF1ZDQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0"
      }
    },
    "node_modules/braces": {
      "version": "3.0.3",
      "resolved": "https://registry.npmjs.org/braces/-/braces-3.0.3.tgz",
      "integrity": "sha512-yQbXgO/OSZVD2IsiLlro+7Hf6Q18EJrKSEsdoMzKePKXct3gvD8oLcOQdIzGupr5Fj+EDe8gO/lxc1BzfMpxvA==",
      "license": "MIT",
      "dependencies": {
        "fill-range": "^7.1.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/browserslist": {
      "version": "4.28.1",
      "resolved": "https://registry.npmjs.org/browserslist/-/browserslist-4.28.1.tgz",
      "integrity": "sha512-ZC5Bd0LgJXgwGqUknZY/vkUQ04r8NXnJZ3yYi4vDmSiZmC/pdSN0NbNRPxZpbtO4uAfDUAFffO8IZoM3Gj8IkA==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "baseline-browser-mapping": "^2.9.0",
        "caniuse-lite": "^1.0.30001759",
        "electron-to-chromium": "^1.5.263",
        "node-releases": "^2.0.27",
        "update-browserslist-db": "^1.2.0"
      },
      "bin": {
        "browserslist": "cli.js"
      },
      "engines": {
        "node": "^6 || ^7 || ^8 || ^9 || ^10 || ^11 || ^12 || >=13.7"
      }
    },
    "node_modules/call-bind": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/call-bind/-/call-bind-1.0.8.tgz",
      "integrity": "sha512-oKlSFMcMwpUg2ednkhQ454wfWiU/ul3CkJe/PEHcTKuiX6RpbehUiFMXu13HalGZxfUwCQzZG747YXBn1im9ww==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.0",
        "es-define-property": "^1.0.0",
        "get-intrinsic": "^1.2.4",
        "set-function-length": "^1.2.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/call-bind-apply-helpers": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/call-bind-apply-helpers/-/call-bind-apply-helpers-1.0.2.tgz",
      "integrity": "sha512-Sp1ablJ0ivDkSzjcaJdxEunN5/XvksFJ2sMBFfq6x0ryhQV/2b/KwFe21cMpmHtPOSij8K99/wSfoEuTObmuMQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "function-bind": "^1.1.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/call-bound": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/call-bound/-/call-bound-1.0.4.tgz",
      "integrity": "sha512-+ys997U96po4Kx/ABpBCqhA9EuxJaQWDQg7295H4hBphv3IZg0boBKuwYpt4YXp6MZ5AmZQnU/tyMTlRpaSejg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.2",
        "get-intrinsic": "^1.3.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/callsites": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/callsites/-/callsites-3.1.0.tgz",
      "integrity": "sha512-P8BjAsXvZS+VIDUI11hHCQEv74YT67YUi5JJFNWIqL235sBmjX4+qx9Muvls5ivyNENctx46xQLQ3aTuE7ssaQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/camelcase-css": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/camelcase-css/-/camelcase-css-2.0.1.tgz",
      "integrity": "sha512-QOSvevhslijgYwRx6Rv7zKdMF8lbRmx+uQGx2+vDc+KI/eBnsy9kit5aj23AgGu3pa4t9AgwbnXWqS+iOY+2aA==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/caniuse-lite": {
      "version": "1.0.30001761",
      "resolved": "https://registry.npmjs.org/caniuse-lite/-/caniuse-lite-1.0.30001761.tgz",
      "integrity": "sha512-JF9ptu1vP2coz98+5051jZ4PwQgd2ni8A+gYSN7EA7dPKIMf0pDlSUxhdmVOaV3/fYK5uWBkgSXJaRLr4+3A6g==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/caniuse-lite"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "CC-BY-4.0"
    },
    "node_modules/chalk": {
      "version": "4.1.2",
      "resolved": "https://registry.npmjs.org/chalk/-/chalk-4.1.2.tgz",
      "integrity": "sha512-oKnbhFyRIXpUuez8iBMmyEa4nbj4IOQyuhc/wy9kY7/WVPcwIO9VA668Pu8RkO7+0G76SLROeyw9CpQ061i4mA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ansi-styles": "^4.1.0",
        "supports-color": "^7.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/chalk/chalk?sponsor=1"
      }
    },
    "node_modules/chokidar": {
      "version": "3.6.0",
      "resolved": "https://registry.npmjs.org/chokidar/-/chokidar-3.6.0.tgz",
      "integrity": "sha512-7VT13fmjotKpGipCW9JEQAusEPE+Ei8nl6/g4FBAmIm0GOOLMua9NDDo/DWp0ZAxCr3cPq5ZpBqmPAQgDda2Pw==",
      "license": "MIT",
      "dependencies": {
        "anymatch": "~3.1.2",
        "braces": "~3.0.2",
        "glob-parent": "~5.1.2",
        "is-binary-path": "~2.1.0",
        "is-glob": "~4.0.1",
        "normalize-path": "~3.0.0",
        "readdirp": "~3.6.0"
      },
      "engines": {
        "node": ">= 8.10.0"
      },
      "funding": {
        "url": "https://paulmillr.com/funding/"
      },
      "optionalDependencies": {
        "fsevents": "~2.3.2"
      }
    },
    "node_modules/chokidar/node_modules/glob-parent": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz",
      "integrity": "sha512-AOIgSQCepiJYwP3ARnGx+5VnTu2HBYdzbGP45eLw1vr3zB3vZLeyed1sC9hnbcOc9/SrMyM5RPQrkGz4aS9Zow==",
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.1"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/client-only": {
      "version": "0.0.1",
      "resolved": "https://registry.npmjs.org/client-only/-/client-only-0.0.1.tgz",
      "integrity": "sha512-IV3Ou0jSMzZrd3pZ48nLkT9DA7Ag1pnPzaiQhpW7c3RbcqqzvzzVu+L8gfqMp/8IM2MQtSiqaCxrrcfu8I8rMA==",
      "license": "MIT"
    },
    "node_modules/clsx": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/clsx/-/clsx-2.1.1.tgz",
      "integrity": "sha512-eYm0QWBtUrBWZWG0d386OGAw16Z995PiOVo2B7bjWSbHedGl5e0ZWaq65kOGgUSNesEIDkB9ISbTg/JK9dhCZA==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/color-convert": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-2.0.1.tgz",
      "integrity": "sha512-RRECPsj7iu/xb5oKYcsFHSppFNnsj/52OVTRKb4zP5onXwVF3zVmmToNcOfGC+CRDpfK/U584fMg38ZHCaElKQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "color-name": "~1.1.4"
      },
      "engines": {
        "node": ">=7.0.0"
      }
    },
    "node_modules/color-name": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.4.tgz",
      "integrity": "sha512-dOy+3AuW3a2wNbZHIuMZpTcgjGuLU/uBL/ubcZF9OXbDo8ff4O8yVp5Bf0efS8uEoYo5q4Fx7dY9OgQGXgAsQA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/commander": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/commander/-/commander-4.1.1.tgz",
      "integrity": "sha512-NOKm8xhkzAjzFx8B2v5OAHT+u5pRQc2UCa2Vq9jYL/31o2wi9mxBA7LIFs3sV5VSC49z6pEhfbMULvShKj26WA==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/concat-map": {
      "version": "0.0.1",
      "resolved": "https://registry.npmjs.org/concat-map/-/concat-map-0.0.1.tgz",
      "integrity": "sha512-/Srv4dswyQNBfohGpz9o6Yb3Gz3SrUDqBH5rTuhGR7ahtlbYKnVxw2bCFMRljaA7EXHaXZ8wsHdodFvbkhKmqg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/convert-source-map": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/convert-source-map/-/convert-source-map-2.0.0.tgz",
      "integrity": "sha512-Kvp459HrV2FEJ1CAsi1Ku+MY3kasH19TFykTz2xWmMeq6bk2NU3XXvfJ+Q61m0xktWwt+1HSYf3JZsTms3aRJg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/cross-spawn": {
      "version": "7.0.6",
      "resolved": "https://registry.npmjs.org/cross-spawn/-/cross-spawn-7.0.6.tgz",
      "integrity": "sha512-uV2QOWP2nWzsy2aMp8aRibhi9dlzF5Hgh5SHaB9OiTGEyDTiJJyx0uy51QXdyWbtAHNua4XJzUKca3OzKUd3vA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "path-key": "^3.1.0",
        "shebang-command": "^2.0.0",
        "which": "^2.0.1"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/cssesc": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/cssesc/-/cssesc-3.0.0.tgz",
      "integrity": "sha512-/Tb/JcjK111nNScGob5MNtsntNM1aCNUDipB/TkwZFhyDrrE47SOx/18wF2bbjgc3ZzCSKW1T5nt5EbFoAz/Vg==",
      "license": "MIT",
      "bin": {
        "cssesc": "bin/cssesc"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/csstype": {
      "version": "3.2.3",
      "resolved": "https://registry.npmjs.org/csstype/-/csstype-3.2.3.tgz",
      "integrity": "sha512-z1HGKcYy2xA8AGQfwrn0PAy+PB7X/GSj3UVJW9qKyn43xWa+gl5nXmU4qqLMRzWVLFC8KusUX8T/0kCiOYpAIQ==",
      "devOptional": true,
      "license": "MIT"
    },
    "node_modules/damerau-levenshtein": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/damerau-levenshtein/-/damerau-levenshtein-1.0.8.tgz",
      "integrity": "sha512-sdQSFB7+llfUcQHUQO3+B8ERRj0Oa4w9POWMI/puGtuf7gFywGmkaLCElnudfTiKZV+NvHqL0ifzdrI8Ro7ESA==",
      "dev": true,
      "license": "BSD-2-Clause"
    },
    "node_modules/data-view-buffer": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/data-view-buffer/-/data-view-buffer-1.0.2.tgz",
      "integrity": "sha512-EmKO5V3OLXh1rtK2wgXRansaK1/mtVdTUEiEI0W8RkvgT05kfxaH29PliLnpLP73yYO6142Q72QNa8Wx/A5CqQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/data-view-byte-length": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/data-view-byte-length/-/data-view-byte-length-1.0.2.tgz",
      "integrity": "sha512-tuhGbE6CfTM9+5ANGf+oQb72Ky/0+s3xKUpHvShfiz2RxMFgFPjsXuRLBVMtvMs15awe45SRb83D6wH4ew6wlQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/inspect-js"
      }
    },
    "node_modules/data-view-byte-offset": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/data-view-byte-offset/-/data-view-byte-offset-1.0.1.tgz",
      "integrity": "sha512-BS8PfmtDGnrgYdOonGZQdLZslWIeCGFP9tpan0hi1Co2Zr2NKADsvGYA8XxuG/4UWgJ6Cjtv+YJnB6MM69QGlQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "is-data-view": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/date-fns": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/date-fns/-/date-fns-4.1.0.tgz",
      "integrity": "sha512-Ukq0owbQXxa/U3EGtsdVBkR1w7KOQ5gIBqdH2hkvknzZPYvBxb/aa6E8L7tmjFtkwZBu3UXBbjIgPo/Ez4xaNg==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/kossnocorp"
      }
    },
    "node_modules/debug": {
      "version": "4.4.3",
      "resolved": "https://registry.npmjs.org/debug/-/debug-4.4.3.tgz",
      "integrity": "sha512-RGwwWnwQvkVfavKVt22FGLw+xYSdzARwm0ru6DhTVA3umU5hZc28V3kO4stgYryrTlLpuvgI9GiijltAjNbcqA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.3"
      },
      "engines": {
        "node": ">=6.0"
      },
      "peerDependenciesMeta": {
        "supports-color": {
          "optional": true
        }
      }
    },
    "node_modules/deep-is": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/deep-is/-/deep-is-0.1.4.tgz",
      "integrity": "sha512-oIPzksmTg4/MriiaYGO+okXDT7ztn/w3Eptv/+gSIdMdKsJo0u4CfYNFJPy+4SKMuCqGw2wxnA+URMg3t8a/bQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/define-data-property": {
      "version": "1.1.4",
      "resolved": "https://registry.npmjs.org/define-data-property/-/define-data-property-1.1.4.tgz",
      "integrity": "sha512-rBMvIzlpA8v6E+SJZoo++HAYqsLrkg7MSfIinMPFhmkorw7X+dOXVJQs+QT69zGkzMyfDnIMN2Wid1+NbL3T+A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-define-property": "^1.0.0",
        "es-errors": "^1.3.0",
        "gopd": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/define-properties": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/define-properties/-/define-properties-1.2.1.tgz",
      "integrity": "sha512-8QmQKqEASLd5nx0U1B1okLElbUuuttJ/AnYmRXbbbGDWh6uS208EjD4Xqq/I9wK7u0v6O08XhTWnt5XtEbR6Dg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.0.1",
        "has-property-descriptors": "^1.0.0",
        "object-keys": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/detect-libc": {
      "version": "2.1.2",
      "resolved": "https://registry.npmjs.org/detect-libc/-/detect-libc-2.1.2.tgz",
      "integrity": "sha512-Btj2BOOO83o3WyH59e8MgXsxEQVcarkUOpEYrubB0urwnN10yQ364rsiByU11nZlqWYZm05i/of7io4mzihBtQ==",
      "license": "Apache-2.0",
      "optional": true,
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/detect-node-es": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/detect-node-es/-/detect-node-es-1.1.0.tgz",
      "integrity": "sha512-ypdmJU/TbBby2Dxibuv7ZLW3Bs1QEmM7nHjEANfohJLvE0XVujisn1qPJcZxg+qDucsr+bP6fLD1rPS3AhJ7EQ==",
      "license": "MIT"
    },
    "node_modules/didyoumean": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/didyoumean/-/didyoumean-1.2.2.tgz",
      "integrity": "sha512-gxtyfqMg7GKyhQmb056K7M3xszy/myH8w+B4RT+QXBQsvAOdc3XymqDDPHx1BgPgsdAA5SIifona89YtRATDzw==",
      "license": "Apache-2.0"
    },
    "node_modules/dlv": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/dlv/-/dlv-1.1.3.tgz",
      "integrity": "sha512-+HlytyjlPKnIG8XuRG8WvmBP8xs8P71y+SKKS6ZXWoEgLuePxtDoUEiH7WkdePWrQ5JBpE6aoVqfZfJUQkjXwA==",
      "license": "MIT"
    },
    "node_modules/doctrine": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/doctrine/-/doctrine-2.1.0.tgz",
      "integrity": "sha512-35mSku4ZXK0vfCuHEDAwt55dg2jNajHZ1odvF+8SSr82EsZY4QmXfuWso8oEd8zRhVObSN18aM0CjSdoBX7zIw==",
      "dev": true,
      "license": "Apache-2.0",
      "dependencies": {
        "esutils": "^2.0.2"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/dunder-proto": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/dunder-proto/-/dunder-proto-1.0.1.tgz",
      "integrity": "sha512-KIN/nDJBQRcXw0MLVhZE9iQHmG68qAVIBg9CqmUYjmQIhgij9U5MFvrqkUL5FbtyyzZuOeOt0zdeRe4UY7ct+A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.1",
        "es-errors": "^1.3.0",
        "gopd": "^1.2.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/electron-to-chromium": {
      "version": "1.5.267",
      "resolved": "https://registry.npmjs.org/electron-to-chromium/-/electron-to-chromium-1.5.267.tgz",
      "integrity": "sha512-0Drusm6MVRXSOJpGbaSVgcQsuB4hEkMpHXaVstcPmhu5LIedxs1xNK/nIxmQIU/RPC0+1/o0AVZfBTkTNJOdUw==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/emoji-regex": {
      "version": "9.2.2",
      "resolved": "https://registry.npmjs.org/emoji-regex/-/emoji-regex-9.2.2.tgz",
      "integrity": "sha512-L18DaJsXSUk2+42pv8mLs5jJT2hqFkFE4j21wOmgbUqsZ2hL72NsUU785g9RXgo3s0ZNgVl42TiHp3ZtOv/Vyg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/es-abstract": {
      "version": "1.24.1",
      "resolved": "https://registry.npmjs.org/es-abstract/-/es-abstract-1.24.1.tgz",
      "integrity": "sha512-zHXBLhP+QehSSbsS9Pt23Gg964240DPd6QCf8WpkqEXxQ7fhdZzYsocOr5u7apWonsS5EjZDmTF+/slGMyasvw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-buffer-byte-length": "^1.0.2",
        "arraybuffer.prototype.slice": "^1.0.4",
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "data-view-buffer": "^1.0.2",
        "data-view-byte-length": "^1.0.2",
        "data-view-byte-offset": "^1.0.1",
        "es-define-property": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.1.1",
        "es-set-tostringtag": "^2.1.0",
        "es-to-primitive": "^1.3.0",
        "function.prototype.name": "^1.1.8",
        "get-intrinsic": "^1.3.0",
        "get-proto": "^1.0.1",
        "get-symbol-description": "^1.1.0",
        "globalthis": "^1.0.4",
        "gopd": "^1.2.0",
        "has-property-descriptors": "^1.0.2",
        "has-proto": "^1.2.0",
        "has-symbols": "^1.1.0",
        "hasown": "^2.0.2",
        "internal-slot": "^1.1.0",
        "is-array-buffer": "^3.0.5",
        "is-callable": "^1.2.7",
        "is-data-view": "^1.0.2",
        "is-negative-zero": "^2.0.3",
        "is-regex": "^1.2.1",
        "is-set": "^2.0.3",
        "is-shared-array-buffer": "^1.0.4",
        "is-string": "^1.1.1",
        "is-typed-array": "^1.1.15",
        "is-weakref": "^1.1.1",
        "math-intrinsics": "^1.1.0",
        "object-inspect": "^1.13.4",
        "object-keys": "^1.1.1",
        "object.assign": "^4.1.7",
        "own-keys": "^1.0.1",
        "regexp.prototype.flags": "^1.5.4",
        "safe-array-concat": "^1.1.3",
        "safe-push-apply": "^1.0.0",
        "safe-regex-test": "^1.1.0",
        "set-proto": "^1.0.0",
        "stop-iteration-iterator": "^1.1.0",
        "string.prototype.trim": "^1.2.10",
        "string.prototype.trimend": "^1.0.9",
        "string.prototype.trimstart": "^1.0.8",
        "typed-array-buffer": "^1.0.3",
        "typed-array-byte-length": "^1.0.3",
        "typed-array-byte-offset": "^1.0.4",
        "typed-array-length": "^1.0.7",
        "unbox-primitive": "^1.1.0",
        "which-typed-array": "^1.1.19"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/es-define-property": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/es-define-property/-/es-define-property-1.0.1.tgz",
      "integrity": "sha512-e3nRfgfUZ4rNGL232gUgX06QNyyez04KdjFrF+LTRoOXmrOgFKDg4BCdsjW8EnT69eqdYGmRpJwiPVYNrCaW3g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-errors": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/es-errors/-/es-errors-1.3.0.tgz",
      "integrity": "sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-iterator-helpers": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/es-iterator-helpers/-/es-iterator-helpers-1.2.2.tgz",
      "integrity": "sha512-BrUQ0cPTB/IwXj23HtwHjS9n7O4h9FX94b4xc5zlTHxeLgTAdzYUDyy6KdExAl9lbN5rtfe44xpjpmj9grxs5w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.24.1",
        "es-errors": "^1.3.0",
        "es-set-tostringtag": "^2.1.0",
        "function-bind": "^1.1.2",
        "get-intrinsic": "^1.3.0",
        "globalthis": "^1.0.4",
        "gopd": "^1.2.0",
        "has-property-descriptors": "^1.0.2",
        "has-proto": "^1.2.0",
        "has-symbols": "^1.1.0",
        "internal-slot": "^1.1.0",
        "iterator.prototype": "^1.1.5",
        "safe-array-concat": "^1.1.3"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-object-atoms": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/es-object-atoms/-/es-object-atoms-1.1.1.tgz",
      "integrity": "sha512-FGgH2h8zKNim9ljj7dankFPcICIK9Cp5bm+c2gQSYePhpaG5+esrLODihIorn+Pe6FGJzWhXQotPv73jTaldXA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-set-tostringtag": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/es-set-tostringtag/-/es-set-tostringtag-2.1.0.tgz",
      "integrity": "sha512-j6vWzfrGVfyXxge+O0x5sh6cvxAog0a/4Rdd2K36zCMV5eJ+/+tOAngRO8cODMNWbVRdVlmGZQL2YS3yR8bIUA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6",
        "has-tostringtag": "^1.0.2",
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-shim-unscopables": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/es-shim-unscopables/-/es-shim-unscopables-1.1.0.tgz",
      "integrity": "sha512-d9T8ucsEhh8Bi1woXCf+TIKDIROLG5WCkxg8geBCbvk22kzwC5G2OnXVMO6FUsvQlgUUXQ2itephWDLqDzbeCw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/es-to-primitive": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/es-to-primitive/-/es-to-primitive-1.3.0.tgz",
      "integrity": "sha512-w+5mJ3GuFL+NjVtJlvydShqE1eN3h3PbI7/5LAsYJP/2qtuMXjfL2LpHSRqo4b4eSF5K/DH1JXKUAHSB2UW50g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-callable": "^1.2.7",
        "is-date-object": "^1.0.5",
        "is-symbol": "^1.0.4"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/escalade": {
      "version": "3.2.0",
      "resolved": "https://registry.npmjs.org/escalade/-/escalade-3.2.0.tgz",
      "integrity": "sha512-WUj2qlxaQtO4g6Pq5c29GTcWGDyd8itL8zTlipgECz3JesAiiOKotd8JU6otB3PACgG6xkJUyVhboMS+bje/jA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/escape-string-regexp": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-4.0.0.tgz",
      "integrity": "sha512-TtpcNJ3XAzx3Gq8sWRzJaVajRs0uVxA2YAkdb1jm2YkPz4G6egUFAyA3n5vtEIZefPk5Wa4UXbKuS5fKkJWdgA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/eslint": {
      "version": "9.39.2",
      "resolved": "https://registry.npmjs.org/eslint/-/eslint-9.39.2.tgz",
      "integrity": "sha512-LEyamqS7W5HB3ujJyvi0HQK/dtVINZvd5mAAp9eT5S/ujByGjiZLCzPcHVzuXbpJDJF/cxwHlfceVUDZ2lnSTw==",
      "dev": true,
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "@eslint-community/eslint-utils": "^4.8.0",
        "@eslint-community/regexpp": "^4.12.1",
        "@eslint/config-array": "^0.21.1",
        "@eslint/config-helpers": "^0.4.2",
        "@eslint/core": "^0.17.0",
        "@eslint/eslintrc": "^3.3.1",
        "@eslint/js": "9.39.2",
        "@eslint/plugin-kit": "^0.4.1",
        "@humanfs/node": "^0.16.6",
        "@humanwhocodes/module-importer": "^1.0.1",
        "@humanwhocodes/retry": "^0.4.2",
        "@types/estree": "^1.0.6",
        "ajv": "^6.12.4",
        "chalk": "^4.0.0",
        "cross-spawn": "^7.0.6",
        "debug": "^4.3.2",
        "escape-string-regexp": "^4.0.0",
        "eslint-scope": "^8.4.0",
        "eslint-visitor-keys": "^4.2.1",
        "espree": "^10.4.0",
        "esquery": "^1.5.0",
        "esutils": "^2.0.2",
        "fast-deep-equal": "^3.1.3",
        "file-entry-cache": "^8.0.0",
        "find-up": "^5.0.0",
        "glob-parent": "^6.0.2",
        "ignore": "^5.2.0",
        "imurmurhash": "^0.1.4",
        "is-glob": "^4.0.0",
        "json-stable-stringify-without-jsonify": "^1.0.1",
        "lodash.merge": "^4.6.2",
        "minimatch": "^3.1.2",
        "natural-compare": "^1.4.0",
        "optionator": "^0.9.3"
      },
      "bin": {
        "eslint": "bin/eslint.js"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://eslint.org/donate"
      },
      "peerDependencies": {
        "jiti": "*"
      },
      "peerDependenciesMeta": {
        "jiti": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-config-next": {
      "version": "16.1.1",
      "resolved": "https://registry.npmjs.org/eslint-config-next/-/eslint-config-next-16.1.1.tgz",
      "integrity": "sha512-55nTpVWm3qeuxoQKLOjQVciKZJUphKrNM0fCcQHAIOGl6VFXgaqeMfv0aKJhs7QtcnlAPhNVqsqRfRjeKBPIUA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@next/eslint-plugin-next": "16.1.1",
        "eslint-import-resolver-node": "^0.3.6",
        "eslint-import-resolver-typescript": "^3.5.2",
        "eslint-plugin-import": "^2.32.0",
        "eslint-plugin-jsx-a11y": "^6.10.0",
        "eslint-plugin-react": "^7.37.0",
        "eslint-plugin-react-hooks": "^7.0.0",
        "globals": "16.4.0",
        "typescript-eslint": "^8.46.0"
      },
      "peerDependencies": {
        "eslint": ">=9.0.0",
        "typescript": ">=3.3.1"
      },
      "peerDependenciesMeta": {
        "typescript": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-config-next/node_modules/globals": {
      "version": "16.4.0",
      "resolved": "https://registry.npmjs.org/globals/-/globals-16.4.0.tgz",
      "integrity": "sha512-ob/2LcVVaVGCYN+r14cnwnoDPUufjiYgSqRhiFD0Q1iI4Odora5RE8Iv1D24hAz5oMophRGkGz+yuvQmmUMnMw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/eslint-import-resolver-node": {
      "version": "0.3.9",
      "resolved": "https://registry.npmjs.org/eslint-import-resolver-node/-/eslint-import-resolver-node-0.3.9.tgz",
      "integrity": "sha512-WFj2isz22JahUv+B788TlO3N6zL3nNJGU8CcZbPZvVEkBPaJdCV4vy5wyghty5ROFbCRnm132v8BScu5/1BQ8g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "debug": "^3.2.7",
        "is-core-module": "^2.13.0",
        "resolve": "^1.22.4"
      }
    },
    "node_modules/eslint-import-resolver-node/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-import-resolver-typescript": {
      "version": "3.10.1",
      "resolved": "https://registry.npmjs.org/eslint-import-resolver-typescript/-/eslint-import-resolver-typescript-3.10.1.tgz",
      "integrity": "sha512-A1rHYb06zjMGAxdLSkN2fXPBwuSaQ0iO5M/hdyS0Ajj1VBaRp0sPD3dn1FhME3c/JluGFbwSxyCfqdSbtQLAHQ==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "@nolyfill/is-core-module": "1.0.39",
        "debug": "^4.4.0",
        "get-tsconfig": "^4.10.0",
        "is-bun-module": "^2.0.0",
        "stable-hash": "^0.0.5",
        "tinyglobby": "^0.2.13",
        "unrs-resolver": "^1.6.2"
      },
      "engines": {
        "node": "^14.18.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint-import-resolver-typescript"
      },
      "peerDependencies": {
        "eslint": "*",
        "eslint-plugin-import": "*",
        "eslint-plugin-import-x": "*"
      },
      "peerDependenciesMeta": {
        "eslint-plugin-import": {
          "optional": true
        },
        "eslint-plugin-import-x": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-module-utils": {
      "version": "2.12.1",
      "resolved": "https://registry.npmjs.org/eslint-module-utils/-/eslint-module-utils-2.12.1.tgz",
      "integrity": "sha512-L8jSWTze7K2mTg0vos/RuLRS5soomksDPoJLXIslC7c8Wmut3bx7CPpJijDcBZtxQ5lrbUdM+s0OlNbz0DCDNw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "debug": "^3.2.7"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependenciesMeta": {
        "eslint": {
          "optional": true
        }
      }
    },
    "node_modules/eslint-module-utils/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-plugin-import": {
      "version": "2.32.0",
      "resolved": "https://registry.npmjs.org/eslint-plugin-import/-/eslint-plugin-import-2.32.0.tgz",
      "integrity": "sha512-whOE1HFo/qJDyX4SnXzP4N6zOWn79WhnCUY/iDR0mPfQZO8wcYE4JClzI2oZrhBnnMUCBCHZhO6VQyoBU95mZA==",
      "dev": true,
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "@rtsao/scc": "^1.1.0",
        "array-includes": "^3.1.9",
        "array.prototype.findlastindex": "^1.2.6",
        "array.prototype.flat": "^1.3.3",
        "array.prototype.flatmap": "^1.3.3",
        "debug": "^3.2.7",
        "doctrine": "^2.1.0",
        "eslint-import-resolver-node": "^0.3.9",
        "eslint-module-utils": "^2.12.1",
        "hasown": "^2.0.2",
        "is-core-module": "^2.16.1",
        "is-glob": "^4.0.3",
        "minimatch": "^3.1.2",
        "object.fromentries": "^2.0.8",
        "object.groupby": "^1.0.3",
        "object.values": "^1.2.1",
        "semver": "^6.3.1",
        "string.prototype.trimend": "^1.0.9",
        "tsconfig-paths": "^3.15.0"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependencies": {
        "eslint": "^2 || ^3 || ^4 || ^5 || ^6 || ^7.2.0 || ^8 || ^9"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/brace-expansion": {
      "version": "1.1.12",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.12.tgz",
      "integrity": "sha512-9T9UjW3r0UW5c1Q7GTwllptXwhvYmEzFhzMfZ9H7FQWt+uZePjZPjBP/W1ZEyZ1twGWom5/56TF4lPcqjnDHcg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/debug": {
      "version": "3.2.7",
      "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.7.tgz",
      "integrity": "sha512-CFjzYYAi4ThfiQvizrFQevTTXHtnCqWfe7x1AhgEscTz6ZbLbfoLRLPugTQyBth6f8ZERVUSyWHFD/7Wu4t1XQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "ms": "^2.1.1"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/minimatch": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz",
      "integrity": "sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/eslint-plugin-import/node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/eslint-plugin-jsx-a11y": {
      "version": "6.10.2",
      "resolved": "https://registry.npmjs.org/eslint-plugin-jsx-a11y/-/eslint-plugin-jsx-a11y-6.10.2.tgz",
      "integrity": "sha512-scB3nz4WmG75pV8+3eRUQOHZlNSUhFNq37xnpgRkCCELU3XMvXAxLk1eqWWyE22Ki4Q01Fnsw9BA3cJHDPgn2Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "aria-query": "^5.3.2",
        "array-includes": "^3.1.8",
        "array.prototype.flatmap": "^1.3.2",
        "ast-types-flow": "^0.0.8",
        "axe-core": "^4.10.0",
        "axobject-query": "^4.1.0",
        "damerau-levenshtein": "^1.0.8",
        "emoji-regex": "^9.2.2",
        "hasown": "^2.0.2",
        "jsx-ast-utils": "^3.3.5",
        "language-tags": "^1.0.9",
        "minimatch": "^3.1.2",
        "object.fromentries": "^2.0.8",
        "safe-regex-test": "^1.0.3",
        "string.prototype.includes": "^2.0.1"
      },
      "engines": {
        "node": ">=4.0"
      },
      "peerDependencies": {
        "eslint": "^3 || ^4 || ^5 || ^6 || ^7 || ^8 || ^9"
      }
    },
    "node_modules/eslint-plugin-jsx-a11y/node_modules/brace-expansion": {
      "version": "1.1.12",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.12.tgz",
      "integrity": "sha512-9T9UjW3r0UW5c1Q7GTwllptXwhvYmEzFhzMfZ9H7FQWt+uZePjZPjBP/W1ZEyZ1twGWom5/56TF4lPcqjnDHcg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/eslint-plugin-jsx-a11y/node_modules/minimatch": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz",
      "integrity": "sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/eslint-plugin-react": {
      "version": "7.37.5",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react/-/eslint-plugin-react-7.37.5.tgz",
      "integrity": "sha512-Qteup0SqU15kdocexFNAJMvCJEfa2xUKNV4CC1xsVMrIIqEy3SQ/rqyxCWNzfrd3/ldy6HMlD2e0JDVpDg2qIA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-includes": "^3.1.8",
        "array.prototype.findlast": "^1.2.5",
        "array.prototype.flatmap": "^1.3.3",
        "array.prototype.tosorted": "^1.1.4",
        "doctrine": "^2.1.0",
        "es-iterator-helpers": "^1.2.1",
        "estraverse": "^5.3.0",
        "hasown": "^2.0.2",
        "jsx-ast-utils": "^2.4.1 || ^3.0.0",
        "minimatch": "^3.1.2",
        "object.entries": "^1.1.9",
        "object.fromentries": "^2.0.8",
        "object.values": "^1.2.1",
        "prop-types": "^15.8.1",
        "resolve": "^2.0.0-next.5",
        "semver": "^6.3.1",
        "string.prototype.matchall": "^4.0.12",
        "string.prototype.repeat": "^1.0.0"
      },
      "engines": {
        "node": ">=4"
      },
      "peerDependencies": {
        "eslint": "^3 || ^4 || ^5 || ^6 || ^7 || ^8 || ^9.7"
      }
    },
    "node_modules/eslint-plugin-react-hooks": {
      "version": "7.0.1",
      "resolved": "https://registry.npmjs.org/eslint-plugin-react-hooks/-/eslint-plugin-react-hooks-7.0.1.tgz",
      "integrity": "sha512-O0d0m04evaNzEPoSW+59Mezf8Qt0InfgGIBJnpC0h3NH/WjUAR7BIKUfysC6todmtiZ/A0oUVS8Gce0WhBrHsA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@babel/core": "^7.24.4",
        "@babel/parser": "^7.24.4",
        "hermes-parser": "^0.25.1",
        "zod": "^3.25.0 || ^4.0.0",
        "zod-validation-error": "^3.5.0 || ^4.0.0"
      },
      "engines": {
        "node": ">=18"
      },
      "peerDependencies": {
        "eslint": "^3.0.0 || ^4.0.0 || ^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0-0 || ^9.0.0"
      }
    },
    "node_modules/eslint-plugin-react/node_modules/brace-expansion": {
      "version": "1.1.12",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.12.tgz",
      "integrity": "sha512-9T9UjW3r0UW5c1Q7GTwllptXwhvYmEzFhzMfZ9H7FQWt+uZePjZPjBP/W1ZEyZ1twGWom5/56TF4lPcqjnDHcg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/eslint-plugin-react/node_modules/minimatch": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz",
      "integrity": "sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/eslint-plugin-react/node_modules/resolve": {
      "version": "2.0.0-next.5",
      "resolved": "https://registry.npmjs.org/resolve/-/resolve-2.0.0-next.5.tgz",
      "integrity": "sha512-U7WjGVG9sH8tvjW5SmGbQuui75FiyjAX72HX15DwBBwF9dNiQZRQAg9nnPhYy+TUnE0+VcrttuvNI8oSxZcocA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-core-module": "^2.13.0",
        "path-parse": "^1.0.7",
        "supports-preserve-symlinks-flag": "^1.0.0"
      },
      "bin": {
        "resolve": "bin/resolve"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/eslint-plugin-react/node_modules/semver": {
      "version": "6.3.1",
      "resolved": "https://registry.npmjs.org/semver/-/semver-6.3.1.tgz",
      "integrity": "sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==",
      "dev": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      }
    },
    "node_modules/eslint-scope": {
      "version": "8.4.0",
      "resolved": "https://registry.npmjs.org/eslint-scope/-/eslint-scope-8.4.0.tgz",
      "integrity": "sha512-sNXOfKCn74rt8RICKMvJS7XKV/Xk9kA7DyJr8mJik3S7Cwgy3qlkkmyS2uQB3jiJg6VNdZd/pDBJu0nvG2NlTg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "esrecurse": "^4.3.0",
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/eslint-visitor-keys": {
      "version": "3.4.3",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-3.4.3.tgz",
      "integrity": "sha512-wpc+LXeiyiisxPlEkUzU6svyS1frIO3Mgxj1fdy7Pm8Ygzguax2N3Fa/D/ag1WqbOprdI+uY6wMUl8/a2G+iag==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^12.22.0 || ^14.17.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/eslint/node_modules/brace-expansion": {
      "version": "1.1.12",
      "resolved": "https://registry.npmjs.org/brace-expansion/-/brace-expansion-1.1.12.tgz",
      "integrity": "sha512-9T9UjW3r0UW5c1Q7GTwllptXwhvYmEzFhzMfZ9H7FQWt+uZePjZPjBP/W1ZEyZ1twGWom5/56TF4lPcqjnDHcg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "balanced-match": "^1.0.0",
        "concat-map": "0.0.1"
      }
    },
    "node_modules/eslint/node_modules/eslint-visitor-keys": {
      "version": "4.2.1",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-4.2.1.tgz",
      "integrity": "sha512-Uhdk5sfqcee/9H/rCOJikYz67o0a2Tw2hGRPOG2Y1R2dg7brRe1uG0yaNQDHu+TO/uQPF/5eCapvYSmHUjt7JQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/eslint/node_modules/ignore": {
      "version": "5.3.2",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-5.3.2.tgz",
      "integrity": "sha512-hsBTNUqQTDwkWtcdYI2i06Y/nUBEsNEDJKjWdigLvegy8kDuJAS8uRlpkkcQpyEXL0Z/pjDy5HBmMjRCJ2gq+g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/eslint/node_modules/minimatch": {
      "version": "3.1.2",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-3.1.2.tgz",
      "integrity": "sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^1.1.7"
      },
      "engines": {
        "node": "*"
      }
    },
    "node_modules/espree": {
      "version": "10.4.0",
      "resolved": "https://registry.npmjs.org/espree/-/espree-10.4.0.tgz",
      "integrity": "sha512-j6PAQ2uUr79PZhBjP5C5fhl8e39FmRnOjsD5lGnWrFU8i2G776tBK7+nP8KuQUTTyAZUwfQqXAgrVH5MbH9CYQ==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "acorn": "^8.15.0",
        "acorn-jsx": "^5.3.2",
        "eslint-visitor-keys": "^4.2.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/espree/node_modules/eslint-visitor-keys": {
      "version": "4.2.1",
      "resolved": "https://registry.npmjs.org/eslint-visitor-keys/-/eslint-visitor-keys-4.2.1.tgz",
      "integrity": "sha512-Uhdk5sfqcee/9H/rCOJikYz67o0a2Tw2hGRPOG2Y1R2dg7brRe1uG0yaNQDHu+TO/uQPF/5eCapvYSmHUjt7JQ==",
      "dev": true,
      "license": "Apache-2.0",
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "url": "https://opencollective.com/eslint"
      }
    },
    "node_modules/esquery": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/esquery/-/esquery-1.6.0.tgz",
      "integrity": "sha512-ca9pw9fomFcKPvFLXhBKUK90ZvGibiGOvRJNbjljY7s7uq/5YO4BOzcYtJqExdx99rF6aAcnRxHmcUHcz6sQsg==",
      "dev": true,
      "license": "BSD-3-Clause",
      "dependencies": {
        "estraverse": "^5.1.0"
      },
      "engines": {
        "node": ">=0.10"
      }
    },
    "node_modules/esrecurse": {
      "version": "4.3.0",
      "resolved": "https://registry.npmjs.org/esrecurse/-/esrecurse-4.3.0.tgz",
      "integrity": "sha512-KmfKL3b6G+RXvP8N1vr3Tq1kL/oCFgn2NYXEtqP8/L3pKapUA4G8cFVaoF3SU323CD4XypR/ffioHmkti6/Tag==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "estraverse": "^5.2.0"
      },
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/estraverse": {
      "version": "5.3.0",
      "resolved": "https://registry.npmjs.org/estraverse/-/estraverse-5.3.0.tgz",
      "integrity": "sha512-MMdARuVEQziNTeJD8DgMqmhwR11BRQ/cBP+pLtYdSTnf3MIO8fFeiINEbX36ZdNlfU/7A9f3gUw49B3oQsvwBA==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/esutils": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/esutils/-/esutils-2.0.3.tgz",
      "integrity": "sha512-kVscqXk4OCp68SZ0dkgEKVi6/8ij300KBWTJq32P/dYeWTSwK41WyTxalN1eRmA5Z9UU/LX9D7FWSmV9SAYx6g==",
      "dev": true,
      "license": "BSD-2-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/fast-deep-equal": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/fast-deep-equal/-/fast-deep-equal-3.1.3.tgz",
      "integrity": "sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5HYNz9cGI++xlpDCIgDaitVs03ATR84Q==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-glob": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/fast-glob/-/fast-glob-3.3.1.tgz",
      "integrity": "sha512-kNFPyjhh5cKjrUltxs+wFx+ZkbRaxxmZ+X0ZU31SOsxCEtP9VPgtq2teZw1DebupL5GmDaNQ6yKMMVcM41iqDg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.stat": "^2.0.2",
        "@nodelib/fs.walk": "^1.2.3",
        "glob-parent": "^5.1.2",
        "merge2": "^1.3.0",
        "micromatch": "^4.0.4"
      },
      "engines": {
        "node": ">=8.6.0"
      }
    },
    "node_modules/fast-glob/node_modules/glob-parent": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz",
      "integrity": "sha512-AOIgSQCepiJYwP3ARnGx+5VnTu2HBYdzbGP45eLw1vr3zB3vZLeyed1sC9hnbcOc9/SrMyM5RPQrkGz4aS9Zow==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.1"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/fast-json-stable-stringify": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/fast-json-stable-stringify/-/fast-json-stable-stringify-2.1.0.tgz",
      "integrity": "sha512-lhd/wF+Lk98HZoTCtlVraHtfh5XYijIjalXck7saUtuanSDyLMxnHhSXEDJqHxD7msR8D0uCmqlkwjCV8xvwHw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fast-levenshtein": {
      "version": "2.0.6",
      "resolved": "https://registry.npmjs.org/fast-levenshtein/-/fast-levenshtein-2.0.6.tgz",
      "integrity": "sha512-DCXu6Ifhqcks7TZKY3Hxp3y6qphY5SJZmrWMDrKcERSOXWQdMhU9Ig/PYrzyw/ul9jOIyh0N4M0tbC5hodg8dw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/fastq": {
      "version": "1.20.1",
      "resolved": "https://registry.npmjs.org/fastq/-/fastq-1.20.1.tgz",
      "integrity": "sha512-GGToxJ/w1x32s/D2EKND7kTil4n8OVk/9mycTc4VDza13lOvpUZTGX3mFSCtV9ksdGBVzvsyAVLM6mHFThxXxw==",
      "license": "ISC",
      "dependencies": {
        "reusify": "^1.0.4"
      }
    },
    "node_modules/file-entry-cache": {
      "version": "8.0.0",
      "resolved": "https://registry.npmjs.org/file-entry-cache/-/file-entry-cache-8.0.0.tgz",
      "integrity": "sha512-XXTUwCvisa5oacNGRP9SfNtYBNAMi+RPwBFmblZEF7N7swHYQS6/Zfk7SRwx4D5j3CH211YNRco1DEMNVfZCnQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flat-cache": "^4.0.0"
      },
      "engines": {
        "node": ">=16.0.0"
      }
    },
    "node_modules/fill-range": {
      "version": "7.1.1",
      "resolved": "https://registry.npmjs.org/fill-range/-/fill-range-7.1.1.tgz",
      "integrity": "sha512-YsGpe3WHLK8ZYi4tWDg2Jy3ebRz2rXowDxnld4bkQB00cc/1Zw9AWnC0i9ztDJitivtQvaI9KaLyKrc+hBW0yg==",
      "license": "MIT",
      "dependencies": {
        "to-regex-range": "^5.0.1"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/find-up": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/find-up/-/find-up-5.0.0.tgz",
      "integrity": "sha512-78/PXT1wlLLDgTzDs7sjq9hzz0vXD+zn+7wypEe4fXQxCmdmqfGsEPQxmiCSQI3ajFV91bVSsvNtrJRiW6nGng==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "locate-path": "^6.0.0",
        "path-exists": "^4.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/flat-cache": {
      "version": "4.0.1",
      "resolved": "https://registry.npmjs.org/flat-cache/-/flat-cache-4.0.1.tgz",
      "integrity": "sha512-f7ccFPK3SXFHpx15UIGyRJ/FJQctuKZ0zVuN3frBo4HnK3cay9VEW0R6yPYFHC0AgqhukPzKjq22t5DmAyqGyw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "flatted": "^3.2.9",
        "keyv": "^4.5.4"
      },
      "engines": {
        "node": ">=16"
      }
    },
    "node_modules/flatted": {
      "version": "3.3.3",
      "resolved": "https://registry.npmjs.org/flatted/-/flatted-3.3.3.tgz",
      "integrity": "sha512-GX+ysw4PBCz0PzosHDepZGANEuFCMLrnRTiEy9McGjmkCQYwRq4A/X786G/fjM/+OjsWSU1ZrY5qyARZmO/uwg==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/for-each": {
      "version": "0.3.5",
      "resolved": "https://registry.npmjs.org/for-each/-/for-each-0.3.5.tgz",
      "integrity": "sha512-dKx12eRCVIzqCxFGplyFKJMPvLEWgmNtUrpTiJIR5u97zEhRG8ySrtboPHZXx7daLxQVrl643cTzbab2tkQjxg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-callable": "^1.2.7"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/fraction.js": {
      "version": "5.3.4",
      "resolved": "https://registry.npmjs.org/fraction.js/-/fraction.js-5.3.4.tgz",
      "integrity": "sha512-1X1NTtiJphryn/uLQz3whtY6jK3fTqoE3ohKs0tT+Ujr1W59oopxmoEh7Lu5p6vBaPbgoM0bzveAW4Qi5RyWDQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": "*"
      },
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/rawify"
      }
    },
    "node_modules/fsevents": {
      "version": "2.3.3",
      "resolved": "https://registry.npmjs.org/fsevents/-/fsevents-2.3.3.tgz",
      "integrity": "sha512-5xoDfX+fL7faATnagmWPpbFtwh/R77WmMMqqHGS65C3vvB0YHrgF+B1YmZ3441tMj5n63k0212XNoJwzlhffQw==",
      "hasInstallScript": true,
      "license": "MIT",
      "optional": true,
      "os": [
        "darwin"
      ],
      "engines": {
        "node": "^8.16.0 || ^10.6.0 || >=11.0.0"
      }
    },
    "node_modules/function-bind": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/function-bind/-/function-bind-1.1.2.tgz",
      "integrity": "sha512-7XHNxH7qX9xG5mIwxkhumTox/MIRNcOgDrxWsMt2pAr23WHp6MrRlN7FBSFpCpr+oVO0F744iUgR82nJMfG2SA==",
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/function.prototype.name": {
      "version": "1.1.8",
      "resolved": "https://registry.npmjs.org/function.prototype.name/-/function.prototype.name-1.1.8.tgz",
      "integrity": "sha512-e5iwyodOHhbMr/yNrc7fDYG4qlbIvI5gajyzPnb5TCwyhjApznQh1BMFou9b30SevY43gCJKXycoCBjMbsuW0Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "functions-have-names": "^1.2.3",
        "hasown": "^2.0.2",
        "is-callable": "^1.2.7"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/functions-have-names": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/functions-have-names/-/functions-have-names-1.2.3.tgz",
      "integrity": "sha512-xckBUXyTIqT97tq2x2AMb+g163b5JFysYk0x4qxNFwbfQkmNZoiRHb6sPzI9/QV33WeuvVYBUIiD4NzNIyqaRQ==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/generator-function": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/generator-function/-/generator-function-2.0.1.tgz",
      "integrity": "sha512-SFdFmIJi+ybC0vjlHN0ZGVGHc3lgE0DxPAT0djjVg+kjOnSqclqmj0KQ7ykTOLP6YxoqOvuAODGdcHJn+43q3g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/gensync": {
      "version": "1.0.0-beta.2",
      "resolved": "https://registry.npmjs.org/gensync/-/gensync-1.0.0-beta.2.tgz",
      "integrity": "sha512-3hN7NaskYvMDLQY55gnW3NQ+mesEAepTqlg+VEbj7zzqEMBVNhzcGYYeqFo/TlYz6eQiFcp1HcsCZO+nGgS8zg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6.9.0"
      }
    },
    "node_modules/get-intrinsic": {
      "version": "1.3.0",
      "resolved": "https://registry.npmjs.org/get-intrinsic/-/get-intrinsic-1.3.0.tgz",
      "integrity": "sha512-9fSjSaos/fRIVIp+xSJlE6lfwhES7LNtKaCBIamHsjr2na1BiABJPo0mOjjz8GJDURarmCPGqaiVg5mfjb98CQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind-apply-helpers": "^1.0.2",
        "es-define-property": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.1.1",
        "function-bind": "^1.1.2",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "has-symbols": "^1.1.0",
        "hasown": "^2.0.2",
        "math-intrinsics": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/get-nonce": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/get-nonce/-/get-nonce-1.0.1.tgz",
      "integrity": "sha512-FJhYRoDaiatfEkUK8HKlicmu/3SGFD51q3itKDGoSTysQJBnfOcxU5GxnhE1E6soB76MbT0MBtnKJuXyAx+96Q==",
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/get-proto": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/get-proto/-/get-proto-1.0.1.tgz",
      "integrity": "sha512-sTSfBjoXBp89JvIKIefqw7U2CCebsc74kiY6awiGogKtoSGbgjYE/G/+l9sF3MWFPNc9IcoOC4ODfKHfxFmp0g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/get-symbol-description": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/get-symbol-description/-/get-symbol-description-1.1.0.tgz",
      "integrity": "sha512-w9UMqWwJxHNOvoNzSJ2oPF5wvYcvP7jUvYzhp67yEhTi17ZDBBC1z9pTdGuzjD+EFIqLSYRweZjqfiPzQ06Ebg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/get-tsconfig": {
      "version": "4.13.0",
      "resolved": "https://registry.npmjs.org/get-tsconfig/-/get-tsconfig-4.13.0.tgz",
      "integrity": "sha512-1VKTZJCwBrvbd+Wn3AOgQP/2Av+TfTCOlE4AcRJE72W1ksZXbAx8PPBR9RzgTeSPzlPMHrbANMH3LbltH73wxQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "resolve-pkg-maps": "^1.0.0"
      },
      "funding": {
        "url": "https://github.com/privatenumber/get-tsconfig?sponsor=1"
      }
    },
    "node_modules/glob-parent": {
      "version": "6.0.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-6.0.2.tgz",
      "integrity": "sha512-XxwI8EOhVQgWp6iDL+3b0r86f4d6AX6zSU55HfB4ydCEuXLXc5FcYeOu+nnGftS4TEju/11rt4KJPTMgbfmv4A==",
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.3"
      },
      "engines": {
        "node": ">=10.13.0"
      }
    },
    "node_modules/globals": {
      "version": "14.0.0",
      "resolved": "https://registry.npmjs.org/globals/-/globals-14.0.0.tgz",
      "integrity": "sha512-oahGvuMGQlPw/ivIYBjVSrWAfWLBeku5tpPE2fOPLi+WHffIWbuh2tCjhyQhTBPMf5E9jDEH4FOmTYgYwbKwtQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/globalthis": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/globalthis/-/globalthis-1.0.4.tgz",
      "integrity": "sha512-DpLKbNU4WylpxJykQujfCcwYWiV/Jhm50Goo0wrVILAv5jOr9d+H+UR3PhSCD2rCCEIg0uc+G+muBTwD54JhDQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-properties": "^1.2.1",
        "gopd": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/gopd": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/gopd/-/gopd-1.2.0.tgz",
      "integrity": "sha512-ZUKRh6/kUFoAiTAtTYPZJ3hw9wNxx+BIBOijnlG9PnrJsCcSjs1wyyD6vJpaYtgnzDrKYRSqf3OO6Rfa93xsRg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-bigints": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/has-bigints/-/has-bigints-1.1.0.tgz",
      "integrity": "sha512-R3pbpkcIqv2Pm3dUwgjclDRVmWpTJW2DcMzcIhEXEx1oh/CEMObMm3KLmRJOdvhM7o4uQBnwr8pzRK2sJWIqfg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-flag": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-4.0.0.tgz",
      "integrity": "sha512-EykJT/Q1KjTWctppgIAgfSO0tKVuZUjhgMr17kqTumMl6Afv3EISleU7qZUzoXDFTAHTDC4NOoG/ZxU3EvlMPQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/has-property-descriptors": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/has-property-descriptors/-/has-property-descriptors-1.0.2.tgz",
      "integrity": "sha512-55JNKuIW+vq4Ke1BjOTjM2YctQIvCT7GFzHwmfZPGo5wnrgkid0YQtnAleFSqumZm4az3n2BS+erby5ipJdgrg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-define-property": "^1.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-proto": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/has-proto/-/has-proto-1.2.0.tgz",
      "integrity": "sha512-KIL7eQPfHQRC8+XluaIw7BHUwwqL19bQn4hzNgdr+1wXoU0KKj6rufu47lhY7KbJR2C6T6+PfyN0Ea7wkSS+qQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-symbols": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/has-symbols/-/has-symbols-1.1.0.tgz",
      "integrity": "sha512-1cDNdwJ2Jaohmb3sg4OmKaMBwuC48sYni5HUw2DvsC8LjGTLK9h+eb1X6RyuOHe4hT0ULCW68iomhjUoKUqlPQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/has-tostringtag": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/has-tostringtag/-/has-tostringtag-1.0.2.tgz",
      "integrity": "sha512-NqADB8VjPFLM2V0VvHUewwwsw0ZWBaIdgo+ieHtK3hasLz4qeCRjYcqfB6AQrBggRKppKF8L52/VqdVsO47Dlw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-symbols": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/hasown": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/hasown/-/hasown-2.0.2.tgz",
      "integrity": "sha512-0hJU9SCPvmMzIBdZFqNPXWa6dqh7WdH0cII9y+CyS8rG3nL48Bclra9HmKhVVUHyPWNH5Y7xDwAB7bfgSjkUMQ==",
      "license": "MIT",
      "dependencies": {
        "function-bind": "^1.1.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/hermes-estree": {
      "version": "0.25.1",
      "resolved": "https://registry.npmjs.org/hermes-estree/-/hermes-estree-0.25.1.tgz",
      "integrity": "sha512-0wUoCcLp+5Ev5pDW2OriHC2MJCbwLwuRx+gAqMTOkGKJJiBCLjtrvy4PWUGn6MIVefecRpzoOZ/UV6iGdOr+Cw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/hermes-parser": {
      "version": "0.25.1",
      "resolved": "https://registry.npmjs.org/hermes-parser/-/hermes-parser-0.25.1.tgz",
      "integrity": "sha512-6pEjquH3rqaI6cYAXYPcz9MS4rY6R4ngRgrgfDshRptUZIc3lw0MCIJIGDj9++mfySOuPTHB4nrSW99BCvOPIA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "hermes-estree": "0.25.1"
      }
    },
    "node_modules/ignore": {
      "version": "7.0.5",
      "resolved": "https://registry.npmjs.org/ignore/-/ignore-7.0.5.tgz",
      "integrity": "sha512-Hs59xBNfUIunMFgWAbGX5cq6893IbWg4KnrjbYwX3tx0ztorVgTDA6B2sxf8ejHJ4wz8BqGUMYlnzNBer5NvGg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 4"
      }
    },
    "node_modules/import-fresh": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/import-fresh/-/import-fresh-3.3.1.tgz",
      "integrity": "sha512-TR3KfrTZTYLPB6jUjfx6MF9WcWrHL9su5TObK4ZkYgBdWKPOFoSoQIdEuTuR82pmtxH2spWG9h6etwfr1pLBqQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "parent-module": "^1.0.0",
        "resolve-from": "^4.0.0"
      },
      "engines": {
        "node": ">=6"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/imurmurhash": {
      "version": "0.1.4",
      "resolved": "https://registry.npmjs.org/imurmurhash/-/imurmurhash-0.1.4.tgz",
      "integrity": "sha512-JmXMZ6wuvDmLiHEml9ykzqO6lwFbof0GG4IkcGaENdCRDDmMVnny7s5HsIgHCbaq0w2MyPhDqkhTUgS2LU2PHA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.8.19"
      }
    },
    "node_modules/internal-slot": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/internal-slot/-/internal-slot-1.1.0.tgz",
      "integrity": "sha512-4gd7VpWNQNB4UKKCFFVcp1AVv+FMOgs9NKzjHKusc8jTMhd5eL1NqQqOpE0KzMds804/yHlglp3uxgluOqAPLw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "hasown": "^2.0.2",
        "side-channel": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/is-array-buffer": {
      "version": "3.0.5",
      "resolved": "https://registry.npmjs.org/is-array-buffer/-/is-array-buffer-3.0.5.tgz",
      "integrity": "sha512-DDfANUiiG2wC1qawP66qlTugJeL5HyzMpfr8lLK+jMQirGzNod0B12cFB/9q838Ru27sBwfw78/rdoU7RERz6A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-async-function": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/is-async-function/-/is-async-function-2.1.1.tgz",
      "integrity": "sha512-9dgM/cZBnNvjzaMYHVoxxfPj2QXt22Ev7SuuPrs+xav0ukGB0S6d4ydZdEiM48kLx5kDV+QBPrpVnFyefL8kkQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "async-function": "^1.0.0",
        "call-bound": "^1.0.3",
        "get-proto": "^1.0.1",
        "has-tostringtag": "^1.0.2",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-bigint": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/is-bigint/-/is-bigint-1.1.0.tgz",
      "integrity": "sha512-n4ZT37wG78iz03xPRKJrHTdZbe3IicyucEtdRsV5yglwc3GyUfbAfpSeD0FJ41NbUNSt5wbhqfp1fS+BgnvDFQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-bigints": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-binary-path": {
      "version": "2.1.0",
      "resolved": "https://registry.npmjs.org/is-binary-path/-/is-binary-path-2.1.0.tgz",
      "integrity": "sha512-ZMERYes6pDydyuGidse7OsHxtbI7WVeUEozgR/g7rd0xUimYNlvZRE/K2MgZTjWy725IfelLeVcEM97mmtRGXw==",
      "license": "MIT",
      "dependencies": {
        "binary-extensions": "^2.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/is-boolean-object": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/is-boolean-object/-/is-boolean-object-1.2.2.tgz",
      "integrity": "sha512-wa56o2/ElJMYqjCjGkXri7it5FbebW5usLw/nPmCMs5DeZ7eziSYZhSmPRn0txqeW4LnAmQQU7FgqLpsEFKM4A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-bun-module": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/is-bun-module/-/is-bun-module-2.0.0.tgz",
      "integrity": "sha512-gNCGbnnnnFAUGKeZ9PdbyeGYJqewpmc2aKHUEMO5nQPWU9lOmv7jcmQIv+qHD8fXW6W7qfuCwX4rY9LNRjXrkQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "semver": "^7.7.1"
      }
    },
    "node_modules/is-callable": {
      "version": "1.2.7",
      "resolved": "https://registry.npmjs.org/is-callable/-/is-callable-1.2.7.tgz",
      "integrity": "sha512-1BC0BVFhS/p0qtw6enp8e+8OD0UrK0oFLztSjNzhcKA3WDuJxxAPXzPuPtKkjEY9UUoEWlX/8fgKeu2S8i9JTA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-core-module": {
      "version": "2.16.1",
      "resolved": "https://registry.npmjs.org/is-core-module/-/is-core-module-2.16.1.tgz",
      "integrity": "sha512-UfoeMA6fIJ8wTYFEUjelnaGI67v6+N7qXJEvQuIGa99l4xsCruSYOVSQ0uPANn4dAzm8lkYPaKLrrijLq7x23w==",
      "license": "MIT",
      "dependencies": {
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-data-view": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/is-data-view/-/is-data-view-1.0.2.tgz",
      "integrity": "sha512-RKtWF8pGmS87i2D6gqQu/l7EYRlVdfzemCJN/P3UOs//x1QE7mfhvzHIApBTRf7axvT6DMGwSwBXYCT0nfB9xw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "get-intrinsic": "^1.2.6",
        "is-typed-array": "^1.1.13"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-date-object": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/is-date-object/-/is-date-object-1.1.0.tgz",
      "integrity": "sha512-PwwhEakHVKTdRNVOw+/Gyh0+MzlCl4R6qKvkhuvLtPMggI1WAHt9sOwZxQLSGpUaDnrdyDsomoRgNnCfKNSXXg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-extglob": {
      "version": "2.1.1",
      "resolved": "https://registry.npmjs.org/is-extglob/-/is-extglob-2.1.1.tgz",
      "integrity": "sha512-SbKbANkN603Vi4jEZv49LeVJMn4yGwsbzZworEoyEiutsN3nJYdbO36zfhGJ6QEDpOZIFkDtnq5JRxmvl3jsoQ==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/is-finalizationregistry": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-finalizationregistry/-/is-finalizationregistry-1.1.1.tgz",
      "integrity": "sha512-1pC6N8qWJbWoPtEjgcL2xyhQOP491EQjeUo3qTKcmV8YSDDJrOepfG8pcC7h/QgnQHYSv0mJ3Z/ZWxmatVrysg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-generator-function": {
      "version": "1.1.2",
      "resolved": "https://registry.npmjs.org/is-generator-function/-/is-generator-function-1.1.2.tgz",
      "integrity": "sha512-upqt1SkGkODW9tsGNG5mtXTXtECizwtS2kA161M+gJPc1xdb/Ax629af6YrTwcOeQHbewrPNlE5Dx7kzvXTizA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.4",
        "generator-function": "^2.0.0",
        "get-proto": "^1.0.1",
        "has-tostringtag": "^1.0.2",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-glob": {
      "version": "4.0.3",
      "resolved": "https://registry.npmjs.org/is-glob/-/is-glob-4.0.3.tgz",
      "integrity": "sha512-xelSayHH36ZgE7ZWhli7pW34hNbNl8Ojv5KVmkJD4hBdD3th8Tfk9vYasLM+mXWOZhFkgZfxhLSnrwRr4elSSg==",
      "license": "MIT",
      "dependencies": {
        "is-extglob": "^2.1.1"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/is-map": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-map/-/is-map-2.0.3.tgz",
      "integrity": "sha512-1Qed0/Hr2m+YqxnM09CjA2d/i6YZNfF6R2oRAOj36eUdS6qIV/huPJNSEpKbupewFs+ZsJlxsjjPbc0/afW6Lw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-negative-zero": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-negative-zero/-/is-negative-zero-2.0.3.tgz",
      "integrity": "sha512-5KoIu2Ngpyek75jXodFvnafB6DJgr3u8uuK0LEZJjrU19DrMD3EVERaR8sjz8CCGgpZvxPl9SuE1GMVPFHx1mw==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-number": {
      "version": "7.0.0",
      "resolved": "https://registry.npmjs.org/is-number/-/is-number-7.0.0.tgz",
      "integrity": "sha512-41Cifkg6e8TylSpdtTpeLVMqvSBEVzTttHvERD741+pnZ8ANv0004MRL43QKPDlK9cGvNp6NZWZUBlbGXYxxng==",
      "license": "MIT",
      "engines": {
        "node": ">=0.12.0"
      }
    },
    "node_modules/is-number-object": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-number-object/-/is-number-object-1.1.1.tgz",
      "integrity": "sha512-lZhclumE1G6VYD8VHe35wFaIif+CTy5SJIi5+3y4psDgWu4wPDoBhF8NxUOinEc7pHgiTsT6MaBb92rKhhD+Xw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-regex": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/is-regex/-/is-regex-1.2.1.tgz",
      "integrity": "sha512-MjYsKHO5O7mCsmRGxWcLWheFqN9DJ/2TmngvjKXihe6efViPqc274+Fx/4fYj/r03+ESvBdTXK0V6tA3rgez1g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "gopd": "^1.2.0",
        "has-tostringtag": "^1.0.2",
        "hasown": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-set": {
      "version": "2.0.3",
      "resolved": "https://registry.npmjs.org/is-set/-/is-set-2.0.3.tgz",
      "integrity": "sha512-iPAjerrse27/ygGLxw+EBR9agv9Y6uLeYVJMu+QNCoouJ1/1ri0mGrcWpfCqFZuzzx3WjtwxG098X+n4OuRkPg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-shared-array-buffer": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/is-shared-array-buffer/-/is-shared-array-buffer-1.0.4.tgz",
      "integrity": "sha512-ISWac8drv4ZGfwKl5slpHG9OwPNty4jOWPRIhBpxOoD+hqITiwuipOQ2bNthAzwA3B4fIjO4Nln74N0S9byq8A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-string": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-string/-/is-string-1.1.1.tgz",
      "integrity": "sha512-BtEeSsoaQjlSPBemMQIrY1MY0uM6vnS1g5fmufYOtnxLGUZM2178PKbhsk7Ffv58IX+ZtcvoGwccYsh0PglkAA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-symbol": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-symbol/-/is-symbol-1.1.1.tgz",
      "integrity": "sha512-9gGx6GTtCQM73BgmHQXfDmLtfjjTUDSyoxTCbp5WtoixAhfgsDirWIcVQ/IHpvI5Vgd5i/J5F7B9cN/WlVbC/w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "has-symbols": "^1.1.0",
        "safe-regex-test": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-typed-array": {
      "version": "1.1.15",
      "resolved": "https://registry.npmjs.org/is-typed-array/-/is-typed-array-1.1.15.tgz",
      "integrity": "sha512-p3EcsicXjit7SaskXHs1hA91QxgTw46Fv6EFKKGS5DRFLD8yKnohjF3hxoju94b/OcMZoQukzpPpBE9uLVKzgQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "which-typed-array": "^1.1.16"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakmap": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/is-weakmap/-/is-weakmap-2.0.2.tgz",
      "integrity": "sha512-K5pXYOm9wqY1RgjpL3YTkF39tni1XajUIkawTLUo9EZEVUFga5gSQJF8nNS7ZwJQ02y+1YCNYcMh+HIf1ZqE+w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakref": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/is-weakref/-/is-weakref-1.1.1.tgz",
      "integrity": "sha512-6i9mGWSlqzNMEqpCp93KwRS1uUOodk2OJ6b+sq7ZPDSy2WuI5NFIxp/254TytR8ftefexkWn5xNiHUNpPOfSew==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/is-weakset": {
      "version": "2.0.4",
      "resolved": "https://registry.npmjs.org/is-weakset/-/is-weakset-2.0.4.tgz",
      "integrity": "sha512-mfcwb6IzQyOKTs84CQMrOwW4gQcaTOAWJ0zzJCl2WSPDrWk/OzDaImWFH3djXhb24g4eudZfLRozAvPGw4d9hQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "get-intrinsic": "^1.2.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/isarray": {
      "version": "2.0.5",
      "resolved": "https://registry.npmjs.org/isarray/-/isarray-2.0.5.tgz",
      "integrity": "sha512-xHjhDr3cNBK0BzdUJSPXZntQUx/mwMS5Rw4A7lPJ90XGAO6ISP/ePDNuo0vhqOZU+UD5JoodwCAAoZQd3FeAKw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/isexe": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/isexe/-/isexe-2.0.0.tgz",
      "integrity": "sha512-RHxMLp9lnKHGHRng9QFhRCMbYAcVpn69smSGcq3f36xjgVVWThj4qqLbTLlq7Ssj8B+fIQ1EuCEGI2lKsyQeIw==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/iterator.prototype": {
      "version": "1.1.5",
      "resolved": "https://registry.npmjs.org/iterator.prototype/-/iterator.prototype-1.1.5.tgz",
      "integrity": "sha512-H0dkQoCa3b2VEeKQBOxFph+JAbcrQdE7KC0UkqwpLmv2EC4P41QXP+rqo9wYodACiG5/WM5s9oDApTU8utwj9g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.6",
        "get-proto": "^1.0.0",
        "has-symbols": "^1.1.0",
        "set-function-name": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/jiti": {
      "version": "1.21.7",
      "resolved": "https://registry.npmjs.org/jiti/-/jiti-1.21.7.tgz",
      "integrity": "sha512-/imKNG4EbWNrVjoNC/1H5/9GFy+tqjGBHCaSsN+P2RnPqjsLmv6UD3Ej+Kj8nBWaRAwyk7kK5ZUc+OEatnTR3A==",
      "license": "MIT",
      "peer": true,
      "bin": {
        "jiti": "bin/jiti.js"
      }
    },
    "node_modules/js-tokens": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/js-tokens/-/js-tokens-4.0.0.tgz",
      "integrity": "sha512-RdJUflcE3cUzKiMqQgsCu06FPu9UdIJO0beYbPhHN4k6apgJtifcoCtT9bcxOpYBtpD2kCM6Sbzg4CausW/PKQ==",
      "license": "MIT"
    },
    "node_modules/js-yaml": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/js-yaml/-/js-yaml-4.1.1.tgz",
      "integrity": "sha512-qQKT4zQxXl8lLwBtHMWwaTcGfFOZviOJet3Oy/xmGk2gZH677CJM9EvtfdSkgWcATZhj/55JZ0rmy3myCT5lsA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "argparse": "^2.0.1"
      },
      "bin": {
        "js-yaml": "bin/js-yaml.js"
      }
    },
    "node_modules/jsesc": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/jsesc/-/jsesc-3.1.0.tgz",
      "integrity": "sha512-/sM3dO2FOzXjKQhJuo0Q173wf2KOo8t4I8vHy6lF9poUp7bKT0/NHE8fPX23PwfhnykfqnC2xRxOnVw5XuGIaA==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "jsesc": "bin/jsesc"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/json-buffer": {
      "version": "3.0.1",
      "resolved": "https://registry.npmjs.org/json-buffer/-/json-buffer-3.0.1.tgz",
      "integrity": "sha512-4bV5BfR2mqfQTJm+V5tPPdf+ZpuhiIvTuAB5g8kcrXOZpTT/QwwVRWBywX1ozr6lEuPdbHxwaJlm9G6mI2sfSQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-schema-traverse": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/json-schema-traverse/-/json-schema-traverse-0.4.1.tgz",
      "integrity": "sha512-xbbCH5dCYU5T8LcEhhuh7HJ88HXuW3qsI3Y0zOZFKfZEHcpWiHU/Jxzk629Brsab/mMiHQti9wMP+845RPe3Vg==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json-stable-stringify-without-jsonify": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/json-stable-stringify-without-jsonify/-/json-stable-stringify-without-jsonify-1.0.1.tgz",
      "integrity": "sha512-Bdboy+l7tA3OGW6FjyFHWkP5LuByj1Tk33Ljyq0axyzdk9//JSi2u3fP1QSmd1KNwq6VOKYGlAu87CisVir6Pw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/json5": {
      "version": "2.2.3",
      "resolved": "https://registry.npmjs.org/json5/-/json5-2.2.3.tgz",
      "integrity": "sha512-XmOWe7eyHYH14cLdVPoyg+GOH3rYX++KpzrylJwSW98t3Nk+U8XOl8FWKOgwtzdb8lXGf6zYwDUzeHMWfxasyg==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "json5": "lib/cli.js"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/jsx-ast-utils": {
      "version": "3.3.5",
      "resolved": "https://registry.npmjs.org/jsx-ast-utils/-/jsx-ast-utils-3.3.5.tgz",
      "integrity": "sha512-ZZow9HBI5O6EPgSJLUb8n2NKgmVWTwCvHGwFuJlMjvLFqlGG6pjirPhtdsseaLZjSibD8eegzmYpUZwoIlj2cQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "array-includes": "^3.1.6",
        "array.prototype.flat": "^1.3.1",
        "object.assign": "^4.1.4",
        "object.values": "^1.1.6"
      },
      "engines": {
        "node": ">=4.0"
      }
    },
    "node_modules/keyv": {
      "version": "4.5.4",
      "resolved": "https://registry.npmjs.org/keyv/-/keyv-4.5.4.tgz",
      "integrity": "sha512-oxVHkHR/EJf2CNXnWxRLW6mg7JyCCUcG0DtEGmL2ctUo1PNTin1PUil+r/+4r5MpVgC/fn1kjsx7mjSujKqIpw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "json-buffer": "3.0.1"
      }
    },
    "node_modules/language-subtag-registry": {
      "version": "0.3.23",
      "resolved": "https://registry.npmjs.org/language-subtag-registry/-/language-subtag-registry-0.3.23.tgz",
      "integrity": "sha512-0K65Lea881pHotoGEa5gDlMxt3pctLi2RplBb7Ezh4rRdLEOtgi7n4EwK9lamnUCkKBqaeKRVebTq6BAxSkpXQ==",
      "dev": true,
      "license": "CC0-1.0"
    },
    "node_modules/language-tags": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/language-tags/-/language-tags-1.0.9.tgz",
      "integrity": "sha512-MbjN408fEndfiQXbFQ1vnd+1NoLDsnQW41410oQBXiyXDMYH5z505juWa4KUE1LqxRC7DgOgZDbKLxHIwm27hA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "language-subtag-registry": "^0.3.20"
      },
      "engines": {
        "node": ">=0.10"
      }
    },
    "node_modules/levn": {
      "version": "0.4.1",
      "resolved": "https://registry.npmjs.org/levn/-/levn-0.4.1.tgz",
      "integrity": "sha512-+bT2uH4E5LGE7h/n3evcS/sQlJXCpIp6ym8OWJ5eV6+67Dsql/LaaT7qJBAt2rzfoa/5QBGBhxDix1dMt2kQKQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1",
        "type-check": "~0.4.0"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/lilconfig": {
      "version": "3.1.3",
      "resolved": "https://registry.npmjs.org/lilconfig/-/lilconfig-3.1.3.tgz",
      "integrity": "sha512-/vlFKAoH5Cgt3Ie+JLhRbwOsCQePABiU3tJ1egGvyQ+33R/vcwM2Zl2QR/LzjsBeItPt3oSVXapn+m4nQDvpzw==",
      "license": "MIT",
      "engines": {
        "node": ">=14"
      },
      "funding": {
        "url": "https://github.com/sponsors/antonk52"
      }
    },
    "node_modules/lines-and-columns": {
      "version": "1.2.4",
      "resolved": "https://registry.npmjs.org/lines-and-columns/-/lines-and-columns-1.2.4.tgz",
      "integrity": "sha512-7ylylesZQ/PV29jhEDl3Ufjo6ZX7gCqJr5F7PKrqc93v7fzSymt1BpwEU8nAUXs8qzzvqhbjhK5QZg6Mt/HkBg==",
      "license": "MIT"
    },
    "node_modules/locate-path": {
      "version": "6.0.0",
      "resolved": "https://registry.npmjs.org/locate-path/-/locate-path-6.0.0.tgz",
      "integrity": "sha512-iPZK6eYjbxRu3uB4/WZ3EsEIMJFMqAoopl3R+zuq0UjcAm/MO6KCweDgPfP3elTztoKP3KtnVHxTn2NHBSDVUw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-locate": "^5.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/lodash.merge": {
      "version": "4.6.2",
      "resolved": "https://registry.npmjs.org/lodash.merge/-/lodash.merge-4.6.2.tgz",
      "integrity": "sha512-0KpjqXRVvrYyCsX1swR/XTK0va6VQkQM6MNo7PqW77ByjAhoARA8EfrP1N4+KlKj8YS0ZUCtRT/YUuhyYDujIQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/loose-envify": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/loose-envify/-/loose-envify-1.4.0.tgz",
      "integrity": "sha512-lyuxPGr/Wfhrlem2CL/UcnUc1zcqKAImBDzukY7Y5F/yQiNdko6+fRLevlw1HgMySw7f611UIY408EtxRSoK3Q==",
      "license": "MIT",
      "dependencies": {
        "js-tokens": "^3.0.0 || ^4.0.0"
      },
      "bin": {
        "loose-envify": "cli.js"
      }
    },
    "node_modules/lru-cache": {
      "version": "5.1.1",
      "resolved": "https://registry.npmjs.org/lru-cache/-/lru-cache-5.1.1.tgz",
      "integrity": "sha512-KpNARQA3Iwv+jTA0utUVVbrh+Jlrr1Fv0e56GGzAFOXN7dk/FviaDW8LHmK52DlcH4WP2n6gI8vN1aesBFgo9w==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "yallist": "^3.0.2"
      }
    },
    "node_modules/lucide-react": {
      "version": "0.562.0",
      "resolved": "https://registry.npmjs.org/lucide-react/-/lucide-react-0.562.0.tgz",
      "integrity": "sha512-82hOAu7y0dbVuFfmO4bYF1XEwYk/mEbM5E+b1jgci/udUBEE/R7LF5Ip0CCEmXe8AybRM8L+04eP+LGZeDvkiw==",
      "license": "ISC",
      "peerDependencies": {
        "react": "^16.5.1 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      }
    },
    "node_modules/math-intrinsics": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/math-intrinsics/-/math-intrinsics-1.1.0.tgz",
      "integrity": "sha512-/IXtbwEk5HTPyEwyKX6hGkYXxM9nbj64B+ilVJnC/R6B0pH5G4V3b0pVbL7DBj4tkhBAppbQUlf6F6Xl9LHu1g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/merge2": {
      "version": "1.4.1",
      "resolved": "https://registry.npmjs.org/merge2/-/merge2-1.4.1.tgz",
      "integrity": "sha512-8q7VEgMJW4J8tcfVPy8g09NcQwZdbwFEqhe/WZkoIzjn/3TGDwtOCYtXGxA3O8tPzpczCCDgv+P2P5y00ZJOOg==",
      "license": "MIT",
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/micromatch": {
      "version": "4.0.8",
      "resolved": "https://registry.npmjs.org/micromatch/-/micromatch-4.0.8.tgz",
      "integrity": "sha512-PXwfBhYu0hBCPw8Dn0E+WDYb7af3dSLVWKi3HGv84IdF4TyFoC0ysxFd0Goxw7nSv4T/PzEJQxsYsEiFCKo2BA==",
      "license": "MIT",
      "dependencies": {
        "braces": "^3.0.3",
        "picomatch": "^2.3.1"
      },
      "engines": {
        "node": ">=8.6"
      }
    },
    "node_modules/minimatch": {
      "version": "9.0.5",
      "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-9.0.5.tgz",
      "integrity": "sha512-G6T0ZX48xgozx7587koeX9Ys2NYy6Gmv//P89sEte9V9whIapMNF4idKxnW2QtCcLiTWlb/wfCabAtAFWhhBow==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "brace-expansion": "^2.0.1"
      },
      "engines": {
        "node": ">=16 || 14 >=14.17"
      },
      "funding": {
        "url": "https://github.com/sponsors/isaacs"
      }
    },
    "node_modules/minimist": {
      "version": "1.2.8",
      "resolved": "https://registry.npmjs.org/minimist/-/minimist-1.2.8.tgz",
      "integrity": "sha512-2yyAR8qBkN3YuheJanUpWC5U3bb5osDywNB8RzDVlDwDHbocAJveqqj1u8+SVD7jkWT4yvsHCpWqqWqAxb0zCA==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/ms": {
      "version": "2.1.3",
      "resolved": "https://registry.npmjs.org/ms/-/ms-2.1.3.tgz",
      "integrity": "sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/mz": {
      "version": "2.7.0",
      "resolved": "https://registry.npmjs.org/mz/-/mz-2.7.0.tgz",
      "integrity": "sha512-z81GNO7nnYMEhrGh9LeymoE4+Yr0Wn5McHIZMK5cfQCl+NDX08sCZgUc9/6MHni9IWuFLm1Z3HTCXu2z9fN62Q==",
      "license": "MIT",
      "dependencies": {
        "any-promise": "^1.0.0",
        "object-assign": "^4.0.1",
        "thenify-all": "^1.0.0"
      }
    },
    "node_modules/nanoid": {
      "version": "3.3.11",
      "resolved": "https://registry.npmjs.org/nanoid/-/nanoid-3.3.11.tgz",
      "integrity": "sha512-N8SpfPUnUp1bK+PMYW8qSWdl9U+wwNWI4QKxOYDy9JAro3WMX7p2OeVRF9v+347pnakNevPmiHhNmZ2HbFA76w==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "bin": {
        "nanoid": "bin/nanoid.cjs"
      },
      "engines": {
        "node": "^10 || ^12 || ^13.7 || ^14 || >=15.0.1"
      }
    },
    "node_modules/napi-postinstall": {
      "version": "0.3.4",
      "resolved": "https://registry.npmjs.org/napi-postinstall/-/napi-postinstall-0.3.4.tgz",
      "integrity": "sha512-PHI5f1O0EP5xJ9gQmFGMS6IZcrVvTjpXjz7Na41gTE7eE2hK11lg04CECCYEEjdc17EV4DO+fkGEtt7TpTaTiQ==",
      "dev": true,
      "license": "MIT",
      "bin": {
        "napi-postinstall": "lib/cli.js"
      },
      "engines": {
        "node": "^12.20.0 || ^14.18.0 || >=16.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/napi-postinstall"
      }
    },
    "node_modules/natural-compare": {
      "version": "1.4.0",
      "resolved": "https://registry.npmjs.org/natural-compare/-/natural-compare-1.4.0.tgz",
      "integrity": "sha512-OWND8ei3VtNC9h7V60qff3SVobHr996CTwgxubgyQYEpg290h9J0buyECNNJexkFm5sOajh5G116RYA1c8ZMSw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/next": {
      "version": "15.5.9",
      "resolved": "https://registry.npmjs.org/next/-/next-15.5.9.tgz",
      "integrity": "sha512-agNLK89seZEtC5zUHwtut0+tNrc0Xw4FT/Dg+B/VLEo9pAcS9rtTKpek3V6kVcVwsB2YlqMaHdfZL4eLEVYuCg==",
      "license": "MIT",
      "dependencies": {
        "@next/env": "15.5.9",
        "@swc/helpers": "0.5.15",
        "caniuse-lite": "^1.0.30001579",
        "postcss": "8.4.31",
        "styled-jsx": "5.1.6"
      },
      "bin": {
        "next": "dist/bin/next"
      },
      "engines": {
        "node": "^18.18.0 || ^19.8.0 || >= 20.0.0"
      },
      "optionalDependencies": {
        "@next/swc-darwin-arm64": "15.5.7",
        "@next/swc-darwin-x64": "15.5.7",
        "@next/swc-linux-arm64-gnu": "15.5.7",
        "@next/swc-linux-arm64-musl": "15.5.7",
        "@next/swc-linux-x64-gnu": "15.5.7",
        "@next/swc-linux-x64-musl": "15.5.7",
        "@next/swc-win32-arm64-msvc": "15.5.7",
        "@next/swc-win32-x64-msvc": "15.5.7",
        "sharp": "^0.34.3"
      },
      "peerDependencies": {
        "@opentelemetry/api": "^1.1.0",
        "@playwright/test": "^1.51.1",
        "babel-plugin-react-compiler": "*",
        "react": "^18.2.0 || 19.0.0-rc-de68d2f4-20241204 || ^19.0.0",
        "react-dom": "^18.2.0 || 19.0.0-rc-de68d2f4-20241204 || ^19.0.0",
        "sass": "^1.3.0"
      },
      "peerDependenciesMeta": {
        "@opentelemetry/api": {
          "optional": true
        },
        "@playwright/test": {
          "optional": true
        },
        "babel-plugin-react-compiler": {
          "optional": true
        },
        "sass": {
          "optional": true
        }
      }
    },
    "node_modules/next/node_modules/postcss": {
      "version": "8.4.31",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.4.31.tgz",
      "integrity": "sha512-PS08Iboia9mts/2ygV3eLpY5ghnUcfLV/EXTOW1E2qYxJKGGBUtNjN76FYHnMs36RmARn41bC0AZmn+rR0OVpQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "nanoid": "^3.3.6",
        "picocolors": "^1.0.0",
        "source-map-js": "^1.0.2"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/node-releases": {
      "version": "2.0.27",
      "resolved": "https://registry.npmjs.org/node-releases/-/node-releases-2.0.27.tgz",
      "integrity": "sha512-nmh3lCkYZ3grZvqcCH+fjmQ7X+H0OeZgP40OierEaAptX4XofMh5kwNbWh7lBduUzCcV/8kZ+NDLCwm2iorIlA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/normalize-path": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/normalize-path/-/normalize-path-3.0.0.tgz",
      "integrity": "sha512-6eZs5Ls3WtCisHWp9S2GUy8dqkpGi4BVSz3GaqiE6ezub0512ESztXUwUB6C6IKbQkY2Pnb/mD4WYojCRwcwLA==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/object-assign": {
      "version": "4.1.1",
      "resolved": "https://registry.npmjs.org/object-assign/-/object-assign-4.1.1.tgz",
      "integrity": "sha512-rJgTQnkUnH1sFw8yT6VSU3zD3sWmu6sZhIseY8VX+GRu3P6F7Fu+JNDoXfklElbLJSnc3FUQHVe4cU5hj+BcUg==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/object-hash": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/object-hash/-/object-hash-3.0.0.tgz",
      "integrity": "sha512-RSn9F68PjH9HqtltsSnqYC1XXoWe9Bju5+213R98cNGttag9q9yAOTzdbsqvIa7aNm5WffBZFpWYr2aWrklWAw==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/object-inspect": {
      "version": "1.13.4",
      "resolved": "https://registry.npmjs.org/object-inspect/-/object-inspect-1.13.4.tgz",
      "integrity": "sha512-W67iLl4J2EXEGTbfeHCffrjDfitvLANg0UlX3wFUUSTx92KXRFegMHUVgSqE+wvhAbi4WqjGg9czysTV2Epbew==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object-keys": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/object-keys/-/object-keys-1.1.1.tgz",
      "integrity": "sha512-NuAESUOUMrlIXOfHKzD6bpPu3tYt3xvjNdRIQ+FeT0lNb4K8WR70CaDxhuNguS2XG+GjkyMwOzsN5ZktImfhLA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.assign": {
      "version": "4.1.7",
      "resolved": "https://registry.npmjs.org/object.assign/-/object.assign-4.1.7.tgz",
      "integrity": "sha512-nK28WOo+QIjBkDduTINE4JkF/UJJKyf2EJxvJKfblDpyg0Q+pkOHNTL0Qwy6NP6FhE/EnzV73BxxqcJaXY9anw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0",
        "has-symbols": "^1.1.0",
        "object-keys": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object.entries": {
      "version": "1.1.9",
      "resolved": "https://registry.npmjs.org/object.entries/-/object.entries-1.1.9.tgz",
      "integrity": "sha512-8u/hfXFRBD1O0hPUjioLhoWFHRmt6tKA4/vZPyckBr18l1KE9uHrFaFaUi8MDRTpi4uak2goyPTSNJLXX2k2Hw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.fromentries": {
      "version": "2.0.8",
      "resolved": "https://registry.npmjs.org/object.fromentries/-/object.fromentries-2.0.8.tgz",
      "integrity": "sha512-k6E21FzySsSK5a21KRADBd/NGneRegFO5pLHfdQLpRDETUNJueLXs3WCzyQ3tFRDYgbq3KHGXfTbi2bs8WQ6rQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/object.groupby": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/object.groupby/-/object.groupby-1.0.3.tgz",
      "integrity": "sha512-+Lhy3TQTuzXI5hevh8sBGqbmurHbbIjAi0Z4S63nthVLmLxfbj4T54a4CfZrXIrt9iP4mVAPYMo/v99taj3wjQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/object.values": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/object.values/-/object.values-1.2.1.tgz",
      "integrity": "sha512-gXah6aZrcUxjWg2zR2MwouP2eHlCBzdV4pygudehaKXSGW4v2AsRQUK+lwwXhii6KFZcunEnmSUoYp5CXibxtA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/optionator": {
      "version": "0.9.4",
      "resolved": "https://registry.npmjs.org/optionator/-/optionator-0.9.4.tgz",
      "integrity": "sha512-6IpQ7mKUxRcZNLIObR0hz7lxsapSSIYNZJwXPGeF0mTVqGKFIXj1DQcMoT22S3ROcLyY/rz0PWaWZ9ayWmad9g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "deep-is": "^0.1.3",
        "fast-levenshtein": "^2.0.6",
        "levn": "^0.4.1",
        "prelude-ls": "^1.2.1",
        "type-check": "^0.4.0",
        "word-wrap": "^1.2.5"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/own-keys": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/own-keys/-/own-keys-1.0.1.tgz",
      "integrity": "sha512-qFOyK5PjiWZd+QQIh+1jhdb9LpxTF0qs7Pm8o5QHYZ0M3vKqSqzsZaEB6oWlxZ+q2sJBMI/Ktgd2N5ZwQoRHfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "get-intrinsic": "^1.2.6",
        "object-keys": "^1.1.1",
        "safe-push-apply": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/p-limit": {
      "version": "3.1.0",
      "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-3.1.0.tgz",
      "integrity": "sha512-TYOanM3wGwNGsZN2cVTYPArw454xnXj5qmWF1bEoAc4+cU/ol7GVh7odevjp1FNHduHc3KZMcFduxU5Xc6uJRQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "yocto-queue": "^0.1.0"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/p-locate": {
      "version": "5.0.0",
      "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-5.0.0.tgz",
      "integrity": "sha512-LaNjtRWUBY++zB5nE/NwcaoMylSPk+S+ZHNB1TzdbMJMny6dynpAGt7X/tl/QYq3TIeE6nxHppbo2LGymrG5Pw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "p-limit": "^3.0.2"
      },
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/parent-module": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/parent-module/-/parent-module-1.0.1.tgz",
      "integrity": "sha512-GQ2EWRpQV8/o+Aw8YqtfZZPfNRWZYkbidE9k5rpl/hC3vtHHBfGm2Ifi6qWV+coDGkrUKZAxE3Lot5kcsRlh+g==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "callsites": "^3.0.0"
      },
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/path-exists": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/path-exists/-/path-exists-4.0.0.tgz",
      "integrity": "sha512-ak9Qy5Q7jYb2Wwcey5Fpvg2KoAc/ZIhLSLOSBmRmygPsGwkVVt0fZa0qrtMz+m6tJTAHfZQ8FnmB4MG4LWy7/w==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-key": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/path-key/-/path-key-3.1.1.tgz",
      "integrity": "sha512-ojmeN0qd+y0jszEtoY48r0Peq5dwMEkIlCOu6Q5f41lfkswXuKtYrhgoTpLnyIcHm24Uhqx+5Tqm2InSwLhE6Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/path-parse": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/path-parse/-/path-parse-1.0.7.tgz",
      "integrity": "sha512-LDJzPVEEEPR+y48z93A0Ed0yXb8pAByGWo/k5YYdYgpY2/2EsOsksJrq7lOHxryrVOn1ejG6oAp8ahvOIQD8sw==",
      "license": "MIT"
    },
    "node_modules/picocolors": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/picocolors/-/picocolors-1.1.1.tgz",
      "integrity": "sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==",
      "license": "ISC"
    },
    "node_modules/picomatch": {
      "version": "2.3.1",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-2.3.1.tgz",
      "integrity": "sha512-JU3teHTNjmE2VCGFzuY8EXzCDVwEqB2a8fsIvwaStHhAWJEeVd1o1QD80CU6+ZdEXXSLbSsuLwJjkCBWqRQUVA==",
      "license": "MIT",
      "engines": {
        "node": ">=8.6"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/pify": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/pify/-/pify-2.3.0.tgz",
      "integrity": "sha512-udgsAY+fTnvv7kI7aaxbqwWNb0AHiB0qBO89PZKPkoTmGOgdbrHDKD+0B2X4uTfJ/FT1R09r9gTsjUjNJotuog==",
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/pirates": {
      "version": "4.0.7",
      "resolved": "https://registry.npmjs.org/pirates/-/pirates-4.0.7.tgz",
      "integrity": "sha512-TfySrs/5nm8fQJDcBDuUng3VOUKsd7S+zqvbOTiGXHfxX4wK31ard+hoNuvkicM/2YFzlpDgABOevKSsB4G/FA==",
      "license": "MIT",
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/possible-typed-array-names": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/possible-typed-array-names/-/possible-typed-array-names-1.1.0.tgz",
      "integrity": "sha512-/+5VFTchJDoVj3bhoqi6UeymcD00DAwb1nJwamzPvHEszJ4FpF6SNNbUbOS8yI56qHzdV8eK0qEfOSiodkTdxg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/postcss": {
      "version": "8.5.6",
      "resolved": "https://registry.npmjs.org/postcss/-/postcss-8.5.6.tgz",
      "integrity": "sha512-3Ybi1tAuwAP9s0r1UQ2J4n5Y0G05bJkpUIO0/bI9MhwmD70S5aTWbXGBwxHrelT+XM1k6dM0pk+SwNkpTRN7Pg==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/postcss"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "nanoid": "^3.3.11",
        "picocolors": "^1.1.1",
        "source-map-js": "^1.2.1"
      },
      "engines": {
        "node": "^10 || ^12 || >=14"
      }
    },
    "node_modules/postcss-import": {
      "version": "15.1.0",
      "resolved": "https://registry.npmjs.org/postcss-import/-/postcss-import-15.1.0.tgz",
      "integrity": "sha512-hpr+J05B2FVYUAXHeK1YyI267J/dDDhMU6B6civm8hSY1jYJnBXxzKDKDswzJmtLHryrjhnDjqqp/49t8FALew==",
      "license": "MIT",
      "dependencies": {
        "postcss-value-parser": "^4.0.0",
        "read-cache": "^1.0.0",
        "resolve": "^1.1.7"
      },
      "engines": {
        "node": ">=14.0.0"
      },
      "peerDependencies": {
        "postcss": "^8.0.0"
      }
    },
    "node_modules/postcss-js": {
      "version": "4.1.0",
      "resolved": "https://registry.npmjs.org/postcss-js/-/postcss-js-4.1.0.tgz",
      "integrity": "sha512-oIAOTqgIo7q2EOwbhb8UalYePMvYoIeRY2YKntdpFQXNosSu3vLrniGgmH9OKs/qAkfoj5oB3le/7mINW1LCfw==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "camelcase-css": "^2.0.1"
      },
      "engines": {
        "node": "^12 || ^14 || >= 16"
      },
      "peerDependencies": {
        "postcss": "^8.4.21"
      }
    },
    "node_modules/postcss-load-config": {
      "version": "6.0.1",
      "resolved": "https://registry.npmjs.org/postcss-load-config/-/postcss-load-config-6.0.1.tgz",
      "integrity": "sha512-oPtTM4oerL+UXmx+93ytZVN82RrlY/wPUV8IeDxFrzIjXOLF1pN+EmKPLbubvKHT2HC20xXsCAH2Z+CKV6Oz/g==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "lilconfig": "^3.1.1"
      },
      "engines": {
        "node": ">= 18"
      },
      "peerDependencies": {
        "jiti": ">=1.21.0",
        "postcss": ">=8.0.9",
        "tsx": "^4.8.1",
        "yaml": "^2.4.2"
      },
      "peerDependenciesMeta": {
        "jiti": {
          "optional": true
        },
        "postcss": {
          "optional": true
        },
        "tsx": {
          "optional": true
        },
        "yaml": {
          "optional": true
        }
      }
    },
    "node_modules/postcss-nested": {
      "version": "6.2.0",
      "resolved": "https://registry.npmjs.org/postcss-nested/-/postcss-nested-6.2.0.tgz",
      "integrity": "sha512-HQbt28KulC5AJzG+cZtj9kvKB93CFCdLvog1WFLf1D+xmMvPGlBstkpTEZfK5+AN9hfJocyBFCNiqyS48bpgzQ==",
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/postcss/"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "postcss-selector-parser": "^6.1.1"
      },
      "engines": {
        "node": ">=12.0"
      },
      "peerDependencies": {
        "postcss": "^8.2.14"
      }
    },
    "node_modules/postcss-selector-parser": {
      "version": "6.1.2",
      "resolved": "https://registry.npmjs.org/postcss-selector-parser/-/postcss-selector-parser-6.1.2.tgz",
      "integrity": "sha512-Q8qQfPiZ+THO/3ZrOrO0cJJKfpYCagtMUkXbnEfmgUjwXg6z/WBeOyS9APBBPCTSiDV+s4SwQGu8yFsiMRIudg==",
      "license": "MIT",
      "dependencies": {
        "cssesc": "^3.0.0",
        "util-deprecate": "^1.0.2"
      },
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/postcss-value-parser": {
      "version": "4.2.0",
      "resolved": "https://registry.npmjs.org/postcss-value-parser/-/postcss-value-parser-4.2.0.tgz",
      "integrity": "sha512-1NNCs6uurfkVbeXG4S8JFT9t19m45ICnif8zWLd5oPSZ50QnwMfK+H3jv408d4jw/7Bttv5axS5IiHoLaVNHeQ==",
      "license": "MIT"
    },
    "node_modules/prelude-ls": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/prelude-ls/-/prelude-ls-1.2.1.tgz",
      "integrity": "sha512-vkcDPrRZo1QZLbn5RLGPpg/WmIQ65qoWWhcGKf/b5eplkkarX0m9z8ppCat4mlOqUsWpyNuYgO3VRyrYHSzX5g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/prop-types": {
      "version": "15.8.1",
      "resolved": "https://registry.npmjs.org/prop-types/-/prop-types-15.8.1.tgz",
      "integrity": "sha512-oj87CgZICdulUohogVAR7AjlC0327U4el4L6eAvOqCeudMDVU0NThNaV+b9Df4dXgSP1gXMTnPdhfe/2qDH5cg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.4.0",
        "object-assign": "^4.1.1",
        "react-is": "^16.13.1"
      }
    },
    "node_modules/punycode": {
      "version": "2.3.1",
      "resolved": "https://registry.npmjs.org/punycode/-/punycode-2.3.1.tgz",
      "integrity": "sha512-vYt7UD1U9Wg6138shLtLOvdAu+8DsC/ilFtEVHcH+wydcSpNE20AfSOduf6MkRFahL5FY7X1oU7nKVZFtfq8Fg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=6"
      }
    },
    "node_modules/queue-microtask": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/queue-microtask/-/queue-microtask-1.2.3.tgz",
      "integrity": "sha512-NuaNSa6flKT5JaSYQzJok04JzTL1CA6aGhv5rfLW3PgqA+M2ChpZQnAC8h8i4ZFkBS8X5RqkDBHA7r4hej3K9A==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT"
    },
    "node_modules/react": {
      "version": "18.3.1",
      "resolved": "https://registry.npmjs.org/react/-/react-18.3.1.tgz",
      "integrity": "sha512-wS+hAgJShR0KhEvPJArfuPVN1+Hz1t0Y6n5jLrGQbkb4urgPE/0Rve+1kMB1v/oWgHgm4WIcV+i7F2pTVj+2iQ==",
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "loose-envify": "^1.1.0"
      },
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/react-dom": {
      "version": "18.3.1",
      "resolved": "https://registry.npmjs.org/react-dom/-/react-dom-18.3.1.tgz",
      "integrity": "sha512-5m4nQKp+rZRb09LNH59GM4BxTh9251/ylbKIbpe7TpGxfJ+9kv6BLkLBXIjjspbgbnIBNqlI23tRnTWT0snUIw==",
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "loose-envify": "^1.1.0",
        "scheduler": "^0.23.2"
      },
      "peerDependencies": {
        "react": "^18.3.1"
      }
    },
    "node_modules/react-is": {
      "version": "16.13.1",
      "resolved": "https://registry.npmjs.org/react-is/-/react-is-16.13.1.tgz",
      "integrity": "sha512-24e6ynE2H+OKt4kqsOvNd8kBpV65zoxbA4BVsEOB3ARVWQki/DHzaUoC5KuON/BiccDaCCTZBuOcfZs70kR8bQ==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/react-remove-scroll": {
      "version": "2.7.2",
      "resolved": "https://registry.npmjs.org/react-remove-scroll/-/react-remove-scroll-2.7.2.tgz",
      "integrity": "sha512-Iqb9NjCCTt6Hf+vOdNIZGdTiH1QSqr27H/Ek9sv/a97gfueI/5h1s3yRi1nngzMUaOOToin5dI1dXKdXiF+u0Q==",
      "license": "MIT",
      "dependencies": {
        "react-remove-scroll-bar": "^2.3.7",
        "react-style-singleton": "^2.2.3",
        "tslib": "^2.1.0",
        "use-callback-ref": "^1.3.3",
        "use-sidecar": "^1.1.3"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/react-remove-scroll-bar": {
      "version": "2.3.8",
      "resolved": "https://registry.npmjs.org/react-remove-scroll-bar/-/react-remove-scroll-bar-2.3.8.tgz",
      "integrity": "sha512-9r+yi9+mgU33AKcj6IbT9oRCO78WriSj6t/cF8DWBZJ9aOGPOTEDvdUDz1FwKim7QXWwmHqtdHnRJfhAxEG46Q==",
      "license": "MIT",
      "dependencies": {
        "react-style-singleton": "^2.2.2",
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/react-style-singleton": {
      "version": "2.2.3",
      "resolved": "https://registry.npmjs.org/react-style-singleton/-/react-style-singleton-2.2.3.tgz",
      "integrity": "sha512-b6jSvxvVnyptAiLjbkWLE/lOnR4lfTtDAl+eUC7RZy+QQWc6wRzIV2CE6xBuMmDxc2qIihtDCZD5NPOFl7fRBQ==",
      "license": "MIT",
      "dependencies": {
        "get-nonce": "^1.0.0",
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/read-cache": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/read-cache/-/read-cache-1.0.0.tgz",
      "integrity": "sha512-Owdv/Ft7IjOgm/i0xvNDZ1LrRANRfew4b2prF3OWMQLxLfu3bS8FVhCsrSCMK4lR56Y9ya+AThoTpDCTxCmpRA==",
      "license": "MIT",
      "dependencies": {
        "pify": "^2.3.0"
      }
    },
    "node_modules/readdirp": {
      "version": "3.6.0",
      "resolved": "https://registry.npmjs.org/readdirp/-/readdirp-3.6.0.tgz",
      "integrity": "sha512-hOS089on8RduqdbhvQ5Z37A0ESjsqz6qnRcffsMU3495FuTdqSm+7bhJ29JvIOsBDEEnan5DPu9t3To9VRlMzA==",
      "license": "MIT",
      "dependencies": {
        "picomatch": "^2.2.1"
      },
      "engines": {
        "node": ">=8.10.0"
      }
    },
    "node_modules/reflect.getprototypeof": {
      "version": "1.0.10",
      "resolved": "https://registry.npmjs.org/reflect.getprototypeof/-/reflect.getprototypeof-1.0.10.tgz",
      "integrity": "sha512-00o4I+DVrefhv+nX0ulyi3biSHCPDe+yLv5o/p6d/UVlirijB8E16FtfwSAi4g3tcqrQ4lRAqQSoFEZJehYEcw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.9",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.7",
        "get-proto": "^1.0.1",
        "which-builtin-type": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/regexp.prototype.flags": {
      "version": "1.5.4",
      "resolved": "https://registry.npmjs.org/regexp.prototype.flags/-/regexp.prototype.flags-1.5.4.tgz",
      "integrity": "sha512-dYqgNSZbDwkaJ2ceRd9ojCGjBq+mOm9LmtXnAnEGyHhN/5R7iDW2TRw3h+o/jCFxus3P2LfWIIiwowAjANm7IA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "define-properties": "^1.2.1",
        "es-errors": "^1.3.0",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "set-function-name": "^2.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/resolve": {
      "version": "1.22.11",
      "resolved": "https://registry.npmjs.org/resolve/-/resolve-1.22.11.tgz",
      "integrity": "sha512-RfqAvLnMl313r7c9oclB1HhUEAezcpLjz95wFH4LVuhk9JF/r22qmVP9AMmOU4vMX7Q8pN8jwNg/CSpdFnMjTQ==",
      "license": "MIT",
      "dependencies": {
        "is-core-module": "^2.16.1",
        "path-parse": "^1.0.7",
        "supports-preserve-symlinks-flag": "^1.0.0"
      },
      "bin": {
        "resolve": "bin/resolve"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/resolve-from": {
      "version": "4.0.0",
      "resolved": "https://registry.npmjs.org/resolve-from/-/resolve-from-4.0.0.tgz",
      "integrity": "sha512-pb/MYmXstAkysRFx8piNI1tGFNQIFA3vkE3Gq4EuA1dF6gHp/+vgZqsCGJapvy8N3Q+4o7FwvquPJcnZ7RYy4g==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/resolve-pkg-maps": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/resolve-pkg-maps/-/resolve-pkg-maps-1.0.0.tgz",
      "integrity": "sha512-seS2Tj26TBVOC2NIc2rOe2y2ZO7efxITtLZcGSOnHHNOQ7CkiUBfw0Iw2ck6xkIhPwLhKNLS8BO+hEpngQlqzw==",
      "dev": true,
      "license": "MIT",
      "funding": {
        "url": "https://github.com/privatenumber/resolve-pkg-maps?sponsor=1"
      }
    },
    "node_modules/reusify": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/reusify/-/reusify-1.1.0.tgz",
      "integrity": "sha512-g6QUff04oZpHs0eG5p83rFLhHeV00ug/Yf9nZM6fLeUrPguBTkTQOdpAWWspMh55TZfVQDPaN3NQJfbVRAxdIw==",
      "license": "MIT",
      "engines": {
        "iojs": ">=1.0.0",
        "node": ">=0.10.0"
      }
    },
    "node_modules/run-parallel": {
      "version": "1.2.0",
      "resolved": "https://registry.npmjs.org/run-parallel/-/run-parallel-1.2.0.tgz",
      "integrity": "sha512-5l4VyZR86LZ/lDxZTR6jqL8AFE2S0IFLMP26AbjsLVADxHdhB/c0GUsH+y39UfCi3dzz8OlQuPmnaJOMoDHQBA==",
      "funding": [
        {
          "type": "github",
          "url": "https://github.com/sponsors/feross"
        },
        {
          "type": "patreon",
          "url": "https://www.patreon.com/feross"
        },
        {
          "type": "consulting",
          "url": "https://feross.org/support"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "queue-microtask": "^1.2.2"
      }
    },
    "node_modules/safe-array-concat": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/safe-array-concat/-/safe-array-concat-1.1.3.tgz",
      "integrity": "sha512-AURm5f0jYEOydBj7VQlVvDrjeFgthDdEF5H1dP+6mNpoXOMo1quQqJ4wvJDyRZ9+pO3kGWoOdmV08cSv2aJV6Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "get-intrinsic": "^1.2.6",
        "has-symbols": "^1.1.0",
        "isarray": "^2.0.5"
      },
      "engines": {
        "node": ">=0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/safe-push-apply": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/safe-push-apply/-/safe-push-apply-1.0.0.tgz",
      "integrity": "sha512-iKE9w/Z7xCzUMIZqdBsp6pEQvwuEebH4vdpjcDWnyzaI6yl6O9FHvVpmGelvEHNsoY6wGblkxR6Zty/h00WiSA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "isarray": "^2.0.5"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/safe-regex-test": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/safe-regex-test/-/safe-regex-test-1.1.0.tgz",
      "integrity": "sha512-x/+Cz4YrimQxQccJf5mKEbIa1NzeCRNI5Ecl/ekmlYaampdNLPalVyIcCZNNH3MvmqBugV5TMYZXv0ljslUlaw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "is-regex": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/scheduler": {
      "version": "0.23.2",
      "resolved": "https://registry.npmjs.org/scheduler/-/scheduler-0.23.2.tgz",
      "integrity": "sha512-UOShsPwz7NrMUqhR6t0hWjFduvOzbtv7toDH1/hIrfRNIDBnnBWd0CwJTGvTpngVlmwGCdP9/Zl/tVrDqcuYzQ==",
      "license": "MIT",
      "dependencies": {
        "loose-envify": "^1.1.0"
      }
    },
    "node_modules/semver": {
      "version": "7.7.3",
      "resolved": "https://registry.npmjs.org/semver/-/semver-7.7.3.tgz",
      "integrity": "sha512-SdsKMrI9TdgjdweUSR9MweHA4EJ8YxHn8DFaDisvhVlUOe4BF1tLD7GAj0lIqWVl+dPb/rExr0Btby5loQm20Q==",
      "devOptional": true,
      "license": "ISC",
      "bin": {
        "semver": "bin/semver.js"
      },
      "engines": {
        "node": ">=10"
      }
    },
    "node_modules/set-function-length": {
      "version": "1.2.2",
      "resolved": "https://registry.npmjs.org/set-function-length/-/set-function-length-1.2.2.tgz",
      "integrity": "sha512-pgRc4hJ4/sNjWCSS9AmnS40x3bNMDTknHgL5UaMBTMyJnU90EgWh1Rz+MC9eFu4BuN/UwZjKQuY/1v3rM7HMfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-errors": "^1.3.0",
        "function-bind": "^1.1.2",
        "get-intrinsic": "^1.2.4",
        "gopd": "^1.0.1",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/set-function-name": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/set-function-name/-/set-function-name-2.0.2.tgz",
      "integrity": "sha512-7PGFlmtwsEADb0WYyvCMa1t+yke6daIG4Wirafur5kcf+MhUnPms1UeR0CKQdTZD81yESwMHbtn+TR+dMviakQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-data-property": "^1.1.4",
        "es-errors": "^1.3.0",
        "functions-have-names": "^1.2.3",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/set-proto": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/set-proto/-/set-proto-1.0.0.tgz",
      "integrity": "sha512-RJRdvCo6IAnPdsvP/7m6bsQqNnn1FCBX5ZNtFL98MmFF/4xAIJTIg1YbHW5DC2W5SKZanrC6i4HsJqlajw/dZw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "dunder-proto": "^1.0.1",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/sharp": {
      "version": "0.34.5",
      "resolved": "https://registry.npmjs.org/sharp/-/sharp-0.34.5.tgz",
      "integrity": "sha512-Ou9I5Ft9WNcCbXrU9cMgPBcCK8LiwLqcbywW3t4oDV37n1pzpuNLsYiAV8eODnjbtQlSDwZ2cUEeQz4E54Hltg==",
      "hasInstallScript": true,
      "license": "Apache-2.0",
      "optional": true,
      "dependencies": {
        "@img/colour": "^1.0.0",
        "detect-libc": "^2.1.2",
        "semver": "^7.7.3"
      },
      "engines": {
        "node": "^18.17.0 || ^20.3.0 || >=21.0.0"
      },
      "funding": {
        "url": "https://opencollective.com/libvips"
      },
      "optionalDependencies": {
        "@img/sharp-darwin-arm64": "0.34.5",
        "@img/sharp-darwin-x64": "0.34.5",
        "@img/sharp-libvips-darwin-arm64": "1.2.4",
        "@img/sharp-libvips-darwin-x64": "1.2.4",
        "@img/sharp-libvips-linux-arm": "1.2.4",
        "@img/sharp-libvips-linux-arm64": "1.2.4",
        "@img/sharp-libvips-linux-ppc64": "1.2.4",
        "@img/sharp-libvips-linux-riscv64": "1.2.4",
        "@img/sharp-libvips-linux-s390x": "1.2.4",
        "@img/sharp-libvips-linux-x64": "1.2.4",
        "@img/sharp-libvips-linuxmusl-arm64": "1.2.4",
        "@img/sharp-libvips-linuxmusl-x64": "1.2.4",
        "@img/sharp-linux-arm": "0.34.5",
        "@img/sharp-linux-arm64": "0.34.5",
        "@img/sharp-linux-ppc64": "0.34.5",
        "@img/sharp-linux-riscv64": "0.34.5",
        "@img/sharp-linux-s390x": "0.34.5",
        "@img/sharp-linux-x64": "0.34.5",
        "@img/sharp-linuxmusl-arm64": "0.34.5",
        "@img/sharp-linuxmusl-x64": "0.34.5",
        "@img/sharp-wasm32": "0.34.5",
        "@img/sharp-win32-arm64": "0.34.5",
        "@img/sharp-win32-ia32": "0.34.5",
        "@img/sharp-win32-x64": "0.34.5"
      }
    },
    "node_modules/shebang-command": {
      "version": "2.0.0",
      "resolved": "https://registry.npmjs.org/shebang-command/-/shebang-command-2.0.0.tgz",
      "integrity": "sha512-kHxr2zZpYtdmrN1qDjrrX/Z1rR1kG8Dx+gkpK1G4eXmvXswmcE1hTWBWYUzlraYw1/yZp6YuDY77YtvbN0dmDA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "shebang-regex": "^3.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/shebang-regex": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/shebang-regex/-/shebang-regex-3.0.0.tgz",
      "integrity": "sha512-7++dFhtcx3353uBaq8DDR4NuxBetBzC7ZQOhmTQInHEd6bSrXdiEyzCvG07Z44UYdLShWUyXt5M/yhz8ekcb1A==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/side-channel": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/side-channel/-/side-channel-1.1.0.tgz",
      "integrity": "sha512-ZX99e6tRweoUXqR+VBrslhda51Nh5MTQwou5tnUDgbtyM0dBgmhEDtWGP/xbKn6hqfPRHujUNwz5fy/wbbhnpw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "object-inspect": "^1.13.3",
        "side-channel-list": "^1.0.0",
        "side-channel-map": "^1.0.1",
        "side-channel-weakmap": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-list": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/side-channel-list/-/side-channel-list-1.0.0.tgz",
      "integrity": "sha512-FCLHtRD/gnpCiCHEiJLOwdmFP+wzCmDEkc9y7NsYxeF4u7Btsn1ZuwgwJGxImImHicJArLP4R0yX4c2KCrMrTA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "object-inspect": "^1.13.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-map": {
      "version": "1.0.1",
      "resolved": "https://registry.npmjs.org/side-channel-map/-/side-channel-map-1.0.1.tgz",
      "integrity": "sha512-VCjCNfgMsby3tTdo02nbjtM/ewra6jPHmpThenkTYh8pG9ucZ/1P8So4u4FGBek/BjpOVsDCMoLA/iuBKIFXRA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.5",
        "object-inspect": "^1.13.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/side-channel-weakmap": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/side-channel-weakmap/-/side-channel-weakmap-1.0.2.tgz",
      "integrity": "sha512-WPS/HvHQTYnHisLo9McqBHOJk2FkHO/tlpvldyrnem4aeQp4hai3gythswg6p01oSoTl58rcpiFAjF2br2Ak2A==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "es-errors": "^1.3.0",
        "get-intrinsic": "^1.2.5",
        "object-inspect": "^1.13.3",
        "side-channel-map": "^1.0.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/source-map-js": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/source-map-js/-/source-map-js-1.2.1.tgz",
      "integrity": "sha512-UXWMKhLOwVKb728IUtQPXxfYU+usdybtUrK/8uGE8CQMvrhOpwvzDBwj0QhSL7MQc7vIsISBG8VQ8+IDQxpfQA==",
      "license": "BSD-3-Clause",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/stable-hash": {
      "version": "0.0.5",
      "resolved": "https://registry.npmjs.org/stable-hash/-/stable-hash-0.0.5.tgz",
      "integrity": "sha512-+L3ccpzibovGXFK+Ap/f8LOS0ahMrHTf3xu7mMLSpEGU0EO9ucaysSylKo9eRDFNhWve/y275iPmIZ4z39a9iA==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/stop-iteration-iterator": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/stop-iteration-iterator/-/stop-iteration-iterator-1.1.0.tgz",
      "integrity": "sha512-eLoXW/DHyl62zxY4SCaIgnRhuMr6ri4juEYARS8E6sCEqzKpOiE521Ucofdx+KnDZl5xmvGYaaKCk5FEOxJCoQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "es-errors": "^1.3.0",
        "internal-slot": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/string.prototype.includes": {
      "version": "2.0.1",
      "resolved": "https://registry.npmjs.org/string.prototype.includes/-/string.prototype.includes-2.0.1.tgz",
      "integrity": "sha512-o7+c9bW6zpAdJHTtujeePODAhkuicdAryFsfVKwA+wGw89wJ4GTY484WTucM9hLtDEOpOvI+aHnzqnC5lHp4Rg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.3"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/string.prototype.matchall": {
      "version": "4.0.12",
      "resolved": "https://registry.npmjs.org/string.prototype.matchall/-/string.prototype.matchall-4.0.12.tgz",
      "integrity": "sha512-6CC9uyBL+/48dYizRf7H7VAYCMCNTBeM78x/VTUe9bFEaxBepPJDa1Ow99LqI/1yF7kuy7Q3cQsYMrcjGUcskA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.3",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.6",
        "es-errors": "^1.3.0",
        "es-object-atoms": "^1.0.0",
        "get-intrinsic": "^1.2.6",
        "gopd": "^1.2.0",
        "has-symbols": "^1.1.0",
        "internal-slot": "^1.1.0",
        "regexp.prototype.flags": "^1.5.3",
        "set-function-name": "^2.0.2",
        "side-channel": "^1.1.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.repeat": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/string.prototype.repeat/-/string.prototype.repeat-1.0.0.tgz",
      "integrity": "sha512-0u/TldDbKD8bFCQ/4f5+mNRrXwZ8hg2w7ZR8wa16e8z9XpePWl3eGEcUD0OXpEH/VJH/2G3gjUtR3ZOiBe2S/w==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "define-properties": "^1.1.3",
        "es-abstract": "^1.17.5"
      }
    },
    "node_modules/string.prototype.trim": {
      "version": "1.2.10",
      "resolved": "https://registry.npmjs.org/string.prototype.trim/-/string.prototype.trim-1.2.10.tgz",
      "integrity": "sha512-Rs66F0P/1kedk5lyYyH9uBzuiI/kNRmwJAR9quK6VOtIpZ2G+hMZd+HQbbv25MgCA6gEffoMZYxlTod4WcdrKA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "define-data-property": "^1.1.4",
        "define-properties": "^1.2.1",
        "es-abstract": "^1.23.5",
        "es-object-atoms": "^1.0.0",
        "has-property-descriptors": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.trimend": {
      "version": "1.0.9",
      "resolved": "https://registry.npmjs.org/string.prototype.trimend/-/string.prototype.trimend-1.0.9.tgz",
      "integrity": "sha512-G7Ok5C6E/j4SGfyLCloXTrngQIQU3PWtXGst3yM7Bea9FRURf1S42ZHlZZtsNque2FN2PoUhfZXYLNWwEr4dLQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.2",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/string.prototype.trimstart": {
      "version": "1.0.8",
      "resolved": "https://registry.npmjs.org/string.prototype.trimstart/-/string.prototype.trimstart-1.0.8.tgz",
      "integrity": "sha512-UXSH262CSZY1tfu3G3Secr6uGLCFVPMhIqHjlgCUtCCcgihYc/xKs9djMTMUOb2j1mVSeU8EU6NWc/iQKU6Gfg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "define-properties": "^1.2.1",
        "es-object-atoms": "^1.0.0"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/strip-bom": {
      "version": "3.0.0",
      "resolved": "https://registry.npmjs.org/strip-bom/-/strip-bom-3.0.0.tgz",
      "integrity": "sha512-vavAMRXOgBVNF6nyEEmL3DBK19iRpDcoIwW+swQ+CbGiu7lju6t+JklA1MHweoWtadgt4ISVUsXLyDq34ddcwA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=4"
      }
    },
    "node_modules/strip-json-comments": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/strip-json-comments/-/strip-json-comments-3.1.1.tgz",
      "integrity": "sha512-6fPc+R4ihwqP6N/aIv2f1gMH8lOVtWQHoqC4yK6oSDVVocumAsfCqjkXnqiYMhmMwS/mEHLp7Vehlt3ql6lEig==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=8"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/styled-jsx": {
      "version": "5.1.6",
      "resolved": "https://registry.npmjs.org/styled-jsx/-/styled-jsx-5.1.6.tgz",
      "integrity": "sha512-qSVyDTeMotdvQYoHWLNGwRFJHC+i+ZvdBRYosOFgC+Wg1vx4frN2/RG/NA7SYqqvKNLf39P2LSRA2pu6n0XYZA==",
      "license": "MIT",
      "dependencies": {
        "client-only": "0.0.1"
      },
      "engines": {
        "node": ">= 12.0.0"
      },
      "peerDependencies": {
        "react": ">= 16.8.0 || 17.x.x || ^18.0.0-0 || ^19.0.0-0"
      },
      "peerDependenciesMeta": {
        "@babel/core": {
          "optional": true
        },
        "babel-plugin-macros": {
          "optional": true
        }
      }
    },
    "node_modules/sucrase": {
      "version": "3.35.1",
      "resolved": "https://registry.npmjs.org/sucrase/-/sucrase-3.35.1.tgz",
      "integrity": "sha512-DhuTmvZWux4H1UOnWMB3sk0sbaCVOoQZjv8u1rDoTV0HTdGem9hkAZtl4JZy8P2z4Bg0nT+YMeOFyVr4zcG5Tw==",
      "license": "MIT",
      "dependencies": {
        "@jridgewell/gen-mapping": "^0.3.2",
        "commander": "^4.0.0",
        "lines-and-columns": "^1.1.6",
        "mz": "^2.7.0",
        "pirates": "^4.0.1",
        "tinyglobby": "^0.2.11",
        "ts-interface-checker": "^0.1.9"
      },
      "bin": {
        "sucrase": "bin/sucrase",
        "sucrase-node": "bin/sucrase-node"
      },
      "engines": {
        "node": ">=16 || 14 >=14.17"
      }
    },
    "node_modules/supports-color": {
      "version": "7.2.0",
      "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-7.2.0.tgz",
      "integrity": "sha512-qpCAvRl9stuOHveKsn7HncJRvv501qIacKzQlO/+Lwxc9+0q2wLyv4Dfvt80/DPn2pqOBsJdDiogXGR9+OvwRw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "has-flag": "^4.0.0"
      },
      "engines": {
        "node": ">=8"
      }
    },
    "node_modules/supports-preserve-symlinks-flag": {
      "version": "1.0.0",
      "resolved": "https://registry.npmjs.org/supports-preserve-symlinks-flag/-/supports-preserve-symlinks-flag-1.0.0.tgz",
      "integrity": "sha512-ot0WnXS9fgdkgIcePe6RHNk1WA8+muPa6cSjeR3V8K27q9BB1rTE3R1p7Hv0z1ZyAc8s6Vvv8DIyWf681MAt0w==",
      "license": "MIT",
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/tailwind-merge": {
      "version": "3.4.0",
      "resolved": "https://registry.npmjs.org/tailwind-merge/-/tailwind-merge-3.4.0.tgz",
      "integrity": "sha512-uSaO4gnW+b3Y2aWoWfFpX62vn2sR3skfhbjsEnaBI81WD1wBLlHZe5sWf0AqjksNdYTbGBEd0UasQMT3SNV15g==",
      "license": "MIT",
      "funding": {
        "type": "github",
        "url": "https://github.com/sponsors/dcastil"
      }
    },
    "node_modules/tailwindcss": {
      "version": "3.4.19",
      "resolved": "https://registry.npmjs.org/tailwindcss/-/tailwindcss-3.4.19.tgz",
      "integrity": "sha512-3ofp+LL8E+pK/JuPLPggVAIaEuhvIz4qNcf3nA1Xn2o/7fb7s/TYpHhwGDv1ZU3PkBluUVaF8PyCHcm48cKLWQ==",
      "license": "MIT",
      "peer": true,
      "dependencies": {
        "@alloc/quick-lru": "^5.2.0",
        "arg": "^5.0.2",
        "chokidar": "^3.6.0",
        "didyoumean": "^1.2.2",
        "dlv": "^1.1.3",
        "fast-glob": "^3.3.2",
        "glob-parent": "^6.0.2",
        "is-glob": "^4.0.3",
        "jiti": "^1.21.7",
        "lilconfig": "^3.1.3",
        "micromatch": "^4.0.8",
        "normalize-path": "^3.0.0",
        "object-hash": "^3.0.0",
        "picocolors": "^1.1.1",
        "postcss": "^8.4.47",
        "postcss-import": "^15.1.0",
        "postcss-js": "^4.0.1",
        "postcss-load-config": "^4.0.2 || ^5.0 || ^6.0",
        "postcss-nested": "^6.2.0",
        "postcss-selector-parser": "^6.1.2",
        "resolve": "^1.22.8",
        "sucrase": "^3.35.0"
      },
      "bin": {
        "tailwind": "lib/cli.js",
        "tailwindcss": "lib/cli.js"
      },
      "engines": {
        "node": ">=14.0.0"
      }
    },
    "node_modules/tailwindcss-animate": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/tailwindcss-animate/-/tailwindcss-animate-1.0.7.tgz",
      "integrity": "sha512-bl6mpH3T7I3UFxuvDEXLxy/VuFxBk5bbzplh7tXI68mwMokNYd1t9qPBHlnyTwfa4JGC4zP516I1hYYtQ/vspA==",
      "license": "MIT",
      "peerDependencies": {
        "tailwindcss": ">=3.0.0 || insiders"
      }
    },
    "node_modules/tailwindcss/node_modules/fast-glob": {
      "version": "3.3.3",
      "resolved": "https://registry.npmjs.org/fast-glob/-/fast-glob-3.3.3.tgz",
      "integrity": "sha512-7MptL8U0cqcFdzIzwOTHoilX9x5BrNqye7Z/LuC7kCMRio1EMSyqRK3BEAUD7sXRq4iT4AzTVuZdhgQ2TCvYLg==",
      "license": "MIT",
      "dependencies": {
        "@nodelib/fs.stat": "^2.0.2",
        "@nodelib/fs.walk": "^1.2.3",
        "glob-parent": "^5.1.2",
        "merge2": "^1.3.0",
        "micromatch": "^4.0.8"
      },
      "engines": {
        "node": ">=8.6.0"
      }
    },
    "node_modules/tailwindcss/node_modules/fast-glob/node_modules/glob-parent": {
      "version": "5.1.2",
      "resolved": "https://registry.npmjs.org/glob-parent/-/glob-parent-5.1.2.tgz",
      "integrity": "sha512-AOIgSQCepiJYwP3ARnGx+5VnTu2HBYdzbGP45eLw1vr3zB3vZLeyed1sC9hnbcOc9/SrMyM5RPQrkGz4aS9Zow==",
      "license": "ISC",
      "dependencies": {
        "is-glob": "^4.0.1"
      },
      "engines": {
        "node": ">= 6"
      }
    },
    "node_modules/thenify": {
      "version": "3.3.1",
      "resolved": "https://registry.npmjs.org/thenify/-/thenify-3.3.1.tgz",
      "integrity": "sha512-RVZSIV5IG10Hk3enotrhvz0T9em6cyHBLkH/YAZuKqd8hRkKhSfCGIcP2KUY0EPxndzANBmNllzWPwak+bheSw==",
      "license": "MIT",
      "dependencies": {
        "any-promise": "^1.0.0"
      }
    },
    "node_modules/thenify-all": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/thenify-all/-/thenify-all-1.6.0.tgz",
      "integrity": "sha512-RNxQH/qI8/t3thXJDwcstUO4zeqo64+Uy/+sNVRBx4Xn2OX+OZ9oP+iJnNFqplFra2ZUVeKCSa2oVWi3T4uVmA==",
      "license": "MIT",
      "dependencies": {
        "thenify": ">= 3.1.0 < 4"
      },
      "engines": {
        "node": ">=0.8"
      }
    },
    "node_modules/tinyglobby": {
      "version": "0.2.15",
      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.15.tgz",
      "integrity": "sha512-j2Zq4NyQYG5XMST4cbs02Ak8iJUdxRM0XI5QyxXuZOzKOINmWurp3smXu3y5wDcJrptwpSjgXHzIQxR0omXljQ==",
      "license": "MIT",
      "dependencies": {
        "fdir": "^6.5.0",
        "picomatch": "^4.0.3"
      },
      "engines": {
        "node": ">=12.0.0"
      },
      "funding": {
        "url": "https://github.com/sponsors/SuperchupuDev"
      }
    },
    "node_modules/tinyglobby/node_modules/fdir": {
      "version": "6.5.0",
      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz",
      "integrity": "sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==",
      "license": "MIT",
      "engines": {
        "node": ">=12.0.0"
      },
      "peerDependencies": {
        "picomatch": "^3 || ^4"
      },
      "peerDependenciesMeta": {
        "picomatch": {
          "optional": true
        }
      }
    },
    "node_modules/tinyglobby/node_modules/picomatch": {
      "version": "4.0.3",
      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.3.tgz",
      "integrity": "sha512-5gTmgEY/sqK6gFXLIsQNH19lWb4ebPDLA4SdLP7dsWkIXHWlG66oPuVvXSGFPppYZz8ZDZq0dYYrbHfBCVUb1Q==",
      "license": "MIT",
      "peer": true,
      "engines": {
        "node": ">=12"
      },
      "funding": {
        "url": "https://github.com/sponsors/jonschlinkert"
      }
    },
    "node_modules/to-regex-range": {
      "version": "5.0.1",
      "resolved": "https://registry.npmjs.org/to-regex-range/-/to-regex-range-5.0.1.tgz",
      "integrity": "sha512-65P7iz6X5yEr1cwcgvQxbbIw7Uk3gOy5dIdtZ4rDveLqhrdJP+Li/Hx6tyK0NEb+2GCyneCMJiGqrADCSNk8sQ==",
      "license": "MIT",
      "dependencies": {
        "is-number": "^7.0.0"
      },
      "engines": {
        "node": ">=8.0"
      }
    },
    "node_modules/ts-api-utils": {
      "version": "2.3.0",
      "resolved": "https://registry.npmjs.org/ts-api-utils/-/ts-api-utils-2.3.0.tgz",
      "integrity": "sha512-6eg3Y9SF7SsAvGzRHQvvc1skDAhwI4YQ32ui1scxD1Ccr0G5qIIbUBT3pFTKX8kmWIQClHobtUdNuaBgwdfdWg==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18.12"
      },
      "peerDependencies": {
        "typescript": ">=4.8.4"
      }
    },
    "node_modules/ts-interface-checker": {
      "version": "0.1.13",
      "resolved": "https://registry.npmjs.org/ts-interface-checker/-/ts-interface-checker-0.1.13.tgz",
      "integrity": "sha512-Y/arvbn+rrz3JCKl9C4kVNfTfSm2/mEp5FSz5EsZSANGPSlQrpRI5M4PKF+mJnE52jOO90PnPSc3Ur3bTQw0gA==",
      "license": "Apache-2.0"
    },
    "node_modules/tsconfig-paths": {
      "version": "3.15.0",
      "resolved": "https://registry.npmjs.org/tsconfig-paths/-/tsconfig-paths-3.15.0.tgz",
      "integrity": "sha512-2Ac2RgzDe/cn48GvOe3M+o82pEFewD3UPbyoUHHdKasHwJKjds4fLXWf/Ux5kATBKN20oaFGu+jbElp1pos0mg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@types/json5": "^0.0.29",
        "json5": "^1.0.2",
        "minimist": "^1.2.6",
        "strip-bom": "^3.0.0"
      }
    },
    "node_modules/tsconfig-paths/node_modules/json5": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/json5/-/json5-1.0.2.tgz",
      "integrity": "sha512-g1MWMLBiz8FKi1e4w0UyVL3w+iJceWAFBAaBnnGKOpNa5f8TLktkbre1+s6oICydWAm+HRUGTmI+//xv2hvXYA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "minimist": "^1.2.0"
      },
      "bin": {
        "json5": "lib/cli.js"
      }
    },
    "node_modules/tslib": {
      "version": "2.8.1",
      "resolved": "https://registry.npmjs.org/tslib/-/tslib-2.8.1.tgz",
      "integrity": "sha512-oJFu94HQb+KVduSUQL7wnpmqnfmLsOA/nAh6b6EH0wCEoK0/mPeXU6c3wKDV83MkOuHPRHtSXKKU99IBazS/2w==",
      "license": "0BSD"
    },
    "node_modules/type-check": {
      "version": "0.4.0",
      "resolved": "https://registry.npmjs.org/type-check/-/type-check-0.4.0.tgz",
      "integrity": "sha512-XleUoc9uwGXqjWwXaUTZAmzMcFZ5858QA2vvx1Ur5xIcixXIP+8LnFDgRplU30us6teqdlskFfu+ae4K79Ooew==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "prelude-ls": "^1.2.1"
      },
      "engines": {
        "node": ">= 0.8.0"
      }
    },
    "node_modules/typed-array-buffer": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/typed-array-buffer/-/typed-array-buffer-1.0.3.tgz",
      "integrity": "sha512-nAYYwfY3qnzX30IkA6AQZjVbtK6duGontcQm1WSG1MD94YLqK0515GNApXkoxKOWMusVssAHWLh9SeaoefYFGw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "es-errors": "^1.3.0",
        "is-typed-array": "^1.1.14"
      },
      "engines": {
        "node": ">= 0.4"
      }
    },
    "node_modules/typed-array-byte-length": {
      "version": "1.0.3",
      "resolved": "https://registry.npmjs.org/typed-array-byte-length/-/typed-array-byte-length-1.0.3.tgz",
      "integrity": "sha512-BaXgOuIxz8n8pIq3e7Atg/7s+DpiYrxn4vdot3w9KbnBhcRQq6o3xemQdIfynqSeXeDrF32x+WvfzmOjPiY9lg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.8",
        "for-each": "^0.3.3",
        "gopd": "^1.2.0",
        "has-proto": "^1.2.0",
        "is-typed-array": "^1.1.14"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typed-array-byte-offset": {
      "version": "1.0.4",
      "resolved": "https://registry.npmjs.org/typed-array-byte-offset/-/typed-array-byte-offset-1.0.4.tgz",
      "integrity": "sha512-bTlAFB/FBYMcuX81gbL4OcpH5PmlFHqlCCpAl8AlEzMz5k53oNDvN8p1PNOWLEmI2x4orp3raOFB51tv9X+MFQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "for-each": "^0.3.3",
        "gopd": "^1.2.0",
        "has-proto": "^1.2.0",
        "is-typed-array": "^1.1.15",
        "reflect.getprototypeof": "^1.0.9"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typed-array-length": {
      "version": "1.0.7",
      "resolved": "https://registry.npmjs.org/typed-array-length/-/typed-array-length-1.0.7.tgz",
      "integrity": "sha512-3KS2b+kL7fsuk/eJZ7EQdnEmQoaho/r6KUef7hxvltNA5DR8NAUM+8wJMbJyZ4G9/7i3v5zPBIMN5aybAh2/Jg==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bind": "^1.0.7",
        "for-each": "^0.3.3",
        "gopd": "^1.0.1",
        "is-typed-array": "^1.1.13",
        "possible-typed-array-names": "^1.0.0",
        "reflect.getprototypeof": "^1.0.6"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/typescript": {
      "version": "5.9.3",
      "resolved": "https://registry.npmjs.org/typescript/-/typescript-5.9.3.tgz",
      "integrity": "sha512-jl1vZzPDinLr9eUt3J/t7V6FgNEw9QjvBPdysz9KfQDD41fQrC2Y4vKQdiaUpFT4bXlb1RHhLpp8wtm6M5TgSw==",
      "dev": true,
      "license": "Apache-2.0",
      "peer": true,
      "bin": {
        "tsc": "bin/tsc",
        "tsserver": "bin/tsserver"
      },
      "engines": {
        "node": ">=14.17"
      }
    },
    "node_modules/typescript-eslint": {
      "version": "8.50.1",
      "resolved": "https://registry.npmjs.org/typescript-eslint/-/typescript-eslint-8.50.1.tgz",
      "integrity": "sha512-ytTHO+SoYSbhAH9CrYnMhiLx8To6PSSvqnvXyPUgPETCvB6eBKmTI9w6XMPS3HsBRGkwTVBX+urA8dYQx6bHfQ==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "@typescript-eslint/eslint-plugin": "8.50.1",
        "@typescript-eslint/parser": "8.50.1",
        "@typescript-eslint/typescript-estree": "8.50.1",
        "@typescript-eslint/utils": "8.50.1"
      },
      "engines": {
        "node": "^18.18.0 || ^20.9.0 || >=21.1.0"
      },
      "funding": {
        "type": "opencollective",
        "url": "https://opencollective.com/typescript-eslint"
      },
      "peerDependencies": {
        "eslint": "^8.57.0 || ^9.0.0",
        "typescript": ">=4.8.4 <6.0.0"
      }
    },
    "node_modules/unbox-primitive": {
      "version": "1.1.0",
      "resolved": "https://registry.npmjs.org/unbox-primitive/-/unbox-primitive-1.1.0.tgz",
      "integrity": "sha512-nWJ91DjeOkej/TA8pXQ3myruKpKEYgqvpw9lz4OPHj/NWFNluYrjbz9j01CJ8yKQd2g4jFoOkINCTW2I5LEEyw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.3",
        "has-bigints": "^1.0.2",
        "has-symbols": "^1.1.0",
        "which-boxed-primitive": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/undici-types": {
      "version": "7.16.0",
      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-7.16.0.tgz",
      "integrity": "sha512-Zz+aZWSj8LE6zoxD+xrjh4VfkIG8Ya6LvYkZqtUQGJPZjYl53ypCaUwWqo7eI0x66KBGeRo+mlBEkMSeSZ38Nw==",
      "dev": true,
      "license": "MIT"
    },
    "node_modules/unrs-resolver": {
      "version": "1.11.1",
      "resolved": "https://registry.npmjs.org/unrs-resolver/-/unrs-resolver-1.11.1.tgz",
      "integrity": "sha512-bSjt9pjaEBnNiGgc9rUiHGKv5l4/TGzDmYw3RhnkJGtLhbnnA/5qJj7x3dNDCRx/PJxu774LlH8lCOlB4hEfKg==",
      "dev": true,
      "hasInstallScript": true,
      "license": "MIT",
      "dependencies": {
        "napi-postinstall": "^0.3.0"
      },
      "funding": {
        "url": "https://opencollective.com/unrs-resolver"
      },
      "optionalDependencies": {
        "@unrs/resolver-binding-android-arm-eabi": "1.11.1",
        "@unrs/resolver-binding-android-arm64": "1.11.1",
        "@unrs/resolver-binding-darwin-arm64": "1.11.1",
        "@unrs/resolver-binding-darwin-x64": "1.11.1",
        "@unrs/resolver-binding-freebsd-x64": "1.11.1",
        "@unrs/resolver-binding-linux-arm-gnueabihf": "1.11.1",
        "@unrs/resolver-binding-linux-arm-musleabihf": "1.11.1",
        "@unrs/resolver-binding-linux-arm64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-arm64-musl": "1.11.1",
        "@unrs/resolver-binding-linux-ppc64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-riscv64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-riscv64-musl": "1.11.1",
        "@unrs/resolver-binding-linux-s390x-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-x64-gnu": "1.11.1",
        "@unrs/resolver-binding-linux-x64-musl": "1.11.1",
        "@unrs/resolver-binding-wasm32-wasi": "1.11.1",
        "@unrs/resolver-binding-win32-arm64-msvc": "1.11.1",
        "@unrs/resolver-binding-win32-ia32-msvc": "1.11.1",
        "@unrs/resolver-binding-win32-x64-msvc": "1.11.1"
      }
    },
    "node_modules/update-browserslist-db": {
      "version": "1.2.3",
      "resolved": "https://registry.npmjs.org/update-browserslist-db/-/update-browserslist-db-1.2.3.tgz",
      "integrity": "sha512-Js0m9cx+qOgDxo0eMiFGEueWztz+d4+M3rGlmKPT+T4IS/jP4ylw3Nwpu6cpTTP8R1MAC1kF4VbdLt3ARf209w==",
      "dev": true,
      "funding": [
        {
          "type": "opencollective",
          "url": "https://opencollective.com/browserslist"
        },
        {
          "type": "tidelift",
          "url": "https://tidelift.com/funding/github/npm/browserslist"
        },
        {
          "type": "github",
          "url": "https://github.com/sponsors/ai"
        }
      ],
      "license": "MIT",
      "dependencies": {
        "escalade": "^3.2.0",
        "picocolors": "^1.1.1"
      },
      "bin": {
        "update-browserslist-db": "cli.js"
      },
      "peerDependencies": {
        "browserslist": ">= 4.21.0"
      }
    },
    "node_modules/uri-js": {
      "version": "4.4.1",
      "resolved": "https://registry.npmjs.org/uri-js/-/uri-js-4.4.1.tgz",
      "integrity": "sha512-7rKUyy33Q1yc98pQ1DAmLtwX109F7TIfWlW1Ydo8Wl1ii1SeHieeh0HHfPeL2fMXK6z0s8ecKs9frCuLJvndBg==",
      "dev": true,
      "license": "BSD-2-Clause",
      "dependencies": {
        "punycode": "^2.1.0"
      }
    },
    "node_modules/use-callback-ref": {
      "version": "1.3.3",
      "resolved": "https://registry.npmjs.org/use-callback-ref/-/use-callback-ref-1.3.3.tgz",
      "integrity": "sha512-jQL3lRnocaFtu3V00JToYz/4QkNWswxijDaCVNZRiRTO3HQDLsdu1ZtmIUvV4yPp+rvWm5j0y0TG/S61cuijTg==",
      "license": "MIT",
      "dependencies": {
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/use-sidecar": {
      "version": "1.1.3",
      "resolved": "https://registry.npmjs.org/use-sidecar/-/use-sidecar-1.1.3.tgz",
      "integrity": "sha512-Fedw0aZvkhynoPYlA5WXrMCAMm+nSWdZt6lzJQ7Ok8S6Q+VsHmHpRWndVRJ8Be0ZbkfPc5LRYH+5XrzXcEeLRQ==",
      "license": "MIT",
      "dependencies": {
        "detect-node-es": "^1.1.0",
        "tslib": "^2.0.0"
      },
      "engines": {
        "node": ">=10"
      },
      "peerDependencies": {
        "@types/react": "*",
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0 || ^19.0.0-rc"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        }
      }
    },
    "node_modules/use-sync-external-store": {
      "version": "1.6.0",
      "resolved": "https://registry.npmjs.org/use-sync-external-store/-/use-sync-external-store-1.6.0.tgz",
      "integrity": "sha512-Pp6GSwGP/NrPIrxVFAIkOQeyw8lFenOHijQWkUTrDvrF4ALqylP2C/KCkeS9dpUM3KvYRQhna5vt7IL95+ZQ9w==",
      "license": "MIT",
      "peerDependencies": {
        "react": "^16.8.0 || ^17.0.0 || ^18.0.0 || ^19.0.0"
      }
    },
    "node_modules/util-deprecate": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/util-deprecate/-/util-deprecate-1.0.2.tgz",
      "integrity": "sha512-EPD5q1uXyFxJpCrLnCc1nHnq3gOa6DZBocAIiI2TaSCA7VCJ1UJDMagCzIkXNsUYfD1daK//LTEQ8xiIbrHtcw==",
      "license": "MIT"
    },
    "node_modules/which": {
      "version": "2.0.2",
      "resolved": "https://registry.npmjs.org/which/-/which-2.0.2.tgz",
      "integrity": "sha512-BLI3Tl1TW3Pvl70l3yq3Y64i+awpwXqsGBYWkkqMtnbXgrMD+yj7rhW0kuEDxzJaYXGjEW5ogapKNMEKNMjibA==",
      "dev": true,
      "license": "ISC",
      "dependencies": {
        "isexe": "^2.0.0"
      },
      "bin": {
        "node-which": "bin/node-which"
      },
      "engines": {
        "node": ">= 8"
      }
    },
    "node_modules/which-boxed-primitive": {
      "version": "1.1.1",
      "resolved": "https://registry.npmjs.org/which-boxed-primitive/-/which-boxed-primitive-1.1.1.tgz",
      "integrity": "sha512-TbX3mj8n0odCBFVlY8AxkqcHASw3L60jIuF8jFP78az3C2YhmGvqbHBpAjTRH2/xqYunrJ9g1jSyjCjpoWzIAA==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-bigint": "^1.1.0",
        "is-boolean-object": "^1.2.1",
        "is-number-object": "^1.1.1",
        "is-string": "^1.1.1",
        "is-symbol": "^1.1.1"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-builtin-type": {
      "version": "1.2.1",
      "resolved": "https://registry.npmjs.org/which-builtin-type/-/which-builtin-type-1.2.1.tgz",
      "integrity": "sha512-6iBczoX+kDQ7a3+YJBnh3T+KZRxM/iYNPXicqk66/Qfm1b93iu+yOImkg0zHbj5LNOcNv1TEADiZ0xa34B4q6Q==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "call-bound": "^1.0.2",
        "function.prototype.name": "^1.1.6",
        "has-tostringtag": "^1.0.2",
        "is-async-function": "^2.0.0",
        "is-date-object": "^1.1.0",
        "is-finalizationregistry": "^1.1.0",
        "is-generator-function": "^1.0.10",
        "is-regex": "^1.2.1",
        "is-weakref": "^1.0.2",
        "isarray": "^2.0.5",
        "which-boxed-primitive": "^1.1.0",
        "which-collection": "^1.0.2",
        "which-typed-array": "^1.1.16"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-collection": {
      "version": "1.0.2",
      "resolved": "https://registry.npmjs.org/which-collection/-/which-collection-1.0.2.tgz",
      "integrity": "sha512-K4jVyjnBdgvc86Y6BkaLZEN933SwYOuBFkdmBu9ZfkcAbdVbpITnDmjvZ/aQjRXQrv5EPkTnD1s39GiiqbngCw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "is-map": "^2.0.3",
        "is-set": "^2.0.3",
        "is-weakmap": "^2.0.2",
        "is-weakset": "^2.0.3"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/which-typed-array": {
      "version": "1.1.19",
      "resolved": "https://registry.npmjs.org/which-typed-array/-/which-typed-array-1.1.19.tgz",
      "integrity": "sha512-rEvr90Bck4WZt9HHFC4DJMsjvu7x+r6bImz0/BrbWb7A2djJ8hnZMrWnHo9F8ssv0OMErasDhftrfROTyqSDrw==",
      "dev": true,
      "license": "MIT",
      "dependencies": {
        "available-typed-arrays": "^1.0.7",
        "call-bind": "^1.0.8",
        "call-bound": "^1.0.4",
        "for-each": "^0.3.5",
        "get-proto": "^1.0.1",
        "gopd": "^1.2.0",
        "has-tostringtag": "^1.0.2"
      },
      "engines": {
        "node": ">= 0.4"
      },
      "funding": {
        "url": "https://github.com/sponsors/ljharb"
      }
    },
    "node_modules/word-wrap": {
      "version": "1.2.5",
      "resolved": "https://registry.npmjs.org/word-wrap/-/word-wrap-1.2.5.tgz",
      "integrity": "sha512-BN22B5eaMMI9UMtjrGd5g5eCYPpCPDUy0FJXbYsaT5zYxjFOckS53SQDE3pWkVoWpHXVb3BrYcEN4Twa55B5cA==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=0.10.0"
      }
    },
    "node_modules/yallist": {
      "version": "3.1.1",
      "resolved": "https://registry.npmjs.org/yallist/-/yallist-3.1.1.tgz",
      "integrity": "sha512-a4UGQaWPH59mOXUYnAG2ewncQS4i4F43Tv3JoAM+s2VDAmS9NsK8GpDMLrCHPksFT7h3K6TOoUNn2pb7RoXx4g==",
      "dev": true,
      "license": "ISC"
    },
    "node_modules/yocto-queue": {
      "version": "0.1.0",
      "resolved": "https://registry.npmjs.org/yocto-queue/-/yocto-queue-0.1.0.tgz",
      "integrity": "sha512-rVksvsnNCdJ/ohGc6xgPwyN8eheCxsiLM8mxuE/t/mOVqJewPuO1miLpTHQiRgTKCLexL4MeAFVagts7HmNZ2Q==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=10"
      },
      "funding": {
        "url": "https://github.com/sponsors/sindresorhus"
      }
    },
    "node_modules/zod": {
      "version": "4.2.1",
      "resolved": "https://registry.npmjs.org/zod/-/zod-4.2.1.tgz",
      "integrity": "sha512-0wZ1IRqGGhMP76gLqz8EyfBXKk0J2qo2+H3fi4mcUP/KtTocoX08nmIAHl1Z2kJIZbZee8KOpBCSNPRgauucjw==",
      "dev": true,
      "license": "MIT",
      "peer": true,
      "funding": {
        "url": "https://github.com/sponsors/colinhacks"
      }
    },
    "node_modules/zod-validation-error": {
      "version": "4.0.2",
      "resolved": "https://registry.npmjs.org/zod-validation-error/-/zod-validation-error-4.0.2.tgz",
      "integrity": "sha512-Q6/nZLe6jxuU80qb/4uJ4t5v2VEZ44lzQjPDhYJNztRQ4wyWc6VF3D3Kb/fAuPetZQnhS3hnajCf9CsWesghLQ==",
      "dev": true,
      "license": "MIT",
      "engines": {
        "node": ">=18.0.0"
      },
      "peerDependencies": {
        "zod": "^3.25.0 || ^4.0.0"
      }
    },
    "node_modules/zustand": {
      "version": "5.0.9",
      "resolved": "https://registry.npmjs.org/zustand/-/zustand-5.0.9.tgz",
      "integrity": "sha512-ALBtUj0AfjJt3uNRQoL1tL2tMvj6Gp/6e39dnfT6uzpelGru8v1tPOGBzayOWbPJvujM8JojDk3E1LxeFisBNg==",
      "license": "MIT",
      "engines": {
        "node": ">=12.20.0"
      },
      "peerDependencies": {
        "@types/react": ">=18.0.0",
        "immer": ">=9.0.6",
        "react": ">=18.0.0",
        "use-sync-external-store": ">=1.2.0"
      },
      "peerDependenciesMeta": {
        "@types/react": {
          "optional": true
        },
        "immer": {
          "optional": true
        },
        "react": {
          "optional": true
        },
        "use-sync-external-store": {
          "optional": true
        }
      }
    }
  }
}

```

# frontend/package.json
```json
{
  "name": "singapore-smb-support-agent-frontend",
  "version": "0.1.0",
  "description": "Frontend for Singapore SMB Customer Support AI Agent",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "@fontsource-variable/inter": "^5.2.5",
    "@fontsource/manrope": "^5.1.3",
    "@radix-ui/react-avatar": "^1.1.11",
    "@radix-ui/react-dialog": "^1.1.15",
    "@radix-ui/react-scroll-area": "^1.2.10",
    "@radix-ui/react-separator": "^1.1.8",
    "@radix-ui/react-slot": "^1.2.4",
    "@tanstack/react-query": "^5.90.14",
    "clsx": "^2.1.1",
    "class-variance-authority": "^0.7.1",
    "date-fns": "^4.1.0",
    "lucide-react": "^0.562.0",
    "next": "^15.5.9",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "tailwind-merge": "^3.4.0",
    "tailwindcss-animate": "^1.0.7",
    "zustand": "^5.0.9"
  },
  "devDependencies": {
    "@types/node": "^25.0.3",
    "@types/react": "^19.2.7",
    "@types/react-dom": "^19.2.3",
    "@typescript-eslint/eslint-plugin": "^8.50.1",
    "@typescript-eslint/parser": "^8.50.1",
    "autoprefixer": "^10.4.23",
    "eslint": "^9.39.2",
    "eslint-config-next": "^16.1.1",
    "postcss": "^8.5.6",
    "tailwindcss": "^3.4.19",
    "typescript": "^5.9.3"
  },
  "engines": {
    "node": ">=20.0.0"
  }
}

```

# frontend/tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"],
      "@/stores/*": ["./src/stores/*"],
      "@/types/*": ["./src/types/*"],
      "@/hooks/*": ["./src/hooks/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}

```

# frontend/next.config.js
```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    optimizePackageImports: ['lucide-react'],
    fontLoaders: [
      { loader: '@next/font/google', options: { subsets: ['latin'] } },
    ],
  },
}

module.exports = nextConfig

```

# frontend/postcss.config.js
```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

```

# frontend/next-env.d.ts
```ts
/// <reference types="next" />
/// <reference types="next/image-types/global" />
/// <reference path="./.next/types/routes.d.ts" />

// NOTE: This file should not be edited
// see https://nextjs.org/docs/app/api-reference/config/typescript for more information.

```

# frontend/tailwind.config.ts
```ts
import type { next } from "next"
import tailwindcssAnimate from "tailwindcss-animate"

const config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        trust: {
          green: "hsl(var(--semantic-green))",
          amber: "hsl(var(--semantic-amber))",
          red: "hsl(var(--semantic-red))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        bounce: {
          "0%, 100%": {
            transform: "translateY(-25%)",
            animationTimingFunction: "cubic-bezier(0.8,0,1,1)",
          },
          "50%": {
            transform: "none",
            animationTimingFunction: "cubic-bezier(0,0,0.2,1)",
          },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "bounce": "bounce 1s infinite",
      },
    },
  },
  plugins: [tailwindcssAnimate],
} satisfies Config

export default config

```

# frontend/Dockerfile
```txt
FROM node:22-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -g nodeuser && adduser -S nodeuser

COPY --from=builder --chown=nodeuser:nodeuser /app/.next/standalone ./
COPY --from=builder --chown=nodeuser:nodeuser /app/.next/static ./.next/static
COPY --from=builder --chown=nodeuser:nodeuser /app/public ./public

USER nodeuser

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]

```

# frontend/src/app/layout.tsx
```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Singapore SMB Support AI Agent',
  description: 'Advanced AI customer support for Singapore businesses',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}

```

# frontend/src/app/page.tsx
```tsx
import { ChatWidget } from '@/components/chat/ChatWidget'

export default function Home() {
  return <ChatWidget />
}

```

# frontend/src/app/globals.css
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Typography - Singapore Professional */
    --font-manrope: 'Manrope', sans-serif;
    --font-inter: 'Inter', sans-serif;

    /* Trust Colors - Singapore Professional */
    --semantic-green: 142 211 142;    /* #8ED38E - Verified */
    --semantic-amber: 251 191 36;     /* #FBBF24 - Warning */
    --semantic-red: 220 38 38;         /* #DC2626 - Error */

    /* Enhanced Radius - Sharp, Professional */
    --radius: 0.125rem;  /* 2px instead of 8px */

    /* Color System - Base */
    --background: 0 0% 100%;
    --foreground: 0 0% 100%;
    --card: 0 0% 100%;
    --card-foreground: 0 0% 100%;
    --popover: 0 0% 100%;
    --popover-foreground: 0 0% 100%;
    --primary: 0 0% 9%;
    --primary-foreground: 0 0% 98%;
    --secondary: 0 0% 96.1%;
    --secondary-foreground: 0 0% 9%;
    --muted: 0 0% 96.1%;
    --muted-foreground: 0 0% 45.1%;
    --accent: 0 0% 96.1%;
    --accent-foreground: 0 0% 9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 89.8%;
    --input: 0 0% 89.8%;
    --ring: 0 0% 3.9%;
  }

  .dark {
    --background: 0 0% 3.9%;
    --foreground: 0 0% 98%;
    --card: 0 0% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 0 0% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 0 0% 9%;
    --secondary: 0 0% 14.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 0 0% 14.9%;
    --muted-foreground: 0 0% 63.9%;
    --accent: 0 0% 14.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 0 0% 14.9%;
    --input: 0 0% 14.9%;
    --ring: 0 0% 83.1%;
  }
}

* {
  @apply border-border;
}

body {
  @apply bg-background text-foreground;
}

```

# frontend/src/components/ui/citation-badge.tsx
```tsx
'use client';

import * as React from 'react';

export interface CitationBadgeProps {
  number: number;
  onClick: () => void;
}

export function CitationBadge({ number, onClick }: CitationBadgeProps) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs font-bold hover:bg-primary/80 transition-colors"
      title="View source"
      type="button"
    >
      [{number}]
    </button>
  );
}

```

# frontend/src/components/ui/textarea.tsx
```tsx
import * as React from 'react';
import { cn } from '@/lib/utils';

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          'flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
          className,
        )}
        ref={ref}
        {...props}
      />
    );
  },
);
Textarea.displayName = 'Textarea';

export { Textarea };

```

# frontend/src/components/ui/card.tsx
```tsx
import * as React from 'react';
import { cn } from '@/lib/utils';

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-lg border bg-card text-card-foreground shadow-sm',
      className,
    )}
    {...props}
  />
));
Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn('text-2xl font-semibold leading-none tracking-tight', className)}
    {...props}
  />
));
CardTitle.displayName = 'CardTitle';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
));
CardContent.displayName = 'CardContent';

export { Card, CardHeader, CardTitle, CardContent };

```

# frontend/src/components/ui/scroll-area.tsx
```tsx
import * as React from 'react';
import { cn } from '@/lib/utils';
import { ScrollAreaProps as RadixScrollAreaProps } from '@radix-ui/react-scroll-area';
import { ScrollArea as RadixScrollArea } from '@radix-ui/react-scroll-area';

const ScrollArea = React.forwardRef<
  HTMLDivElement,
  RadixScrollAreaProps
>(({ className, children, ...props }, ref) => (
  <RadixScrollArea
    ref={ref}
    className={cn('relative overflow-hidden', className)}
    {...props}
  >
    <RadixScrollArea.Viewport className="h-full w-full rounded-[inherit]">
      {children}
    </RadixScrollArea.Viewport>
    <RadixScrollArea.Scrollbar
      className="flex touch-none select-none transition-colors"
      orientation="vertical"
    >
      <RadixScrollArea.Thumb className="relative flex-1 w-2.5 rounded-full bg-border" />
    </RadixScrollArea.Scrollbar>
    <RadixScrollArea.Scrollbar
      className="flex touch-none select-none transition-colors"
      orientation="horizontal"
    >
      <RadixScrollArea.Thumb className="relative flex-1 h-2.5 rounded-full bg-border" />
    </RadixScrollArea.Scrollbar>
  </RadixScrollArea>
));
ScrollArea.displayName = 'ScrollArea';

export { ScrollArea };

```

# frontend/src/components/ui/badge.tsx
```tsx
import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
  {
    variants: {
      variant: {
        default:
          'border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80',
        secondary:
          'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        destructive:
          'border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80',
        outline: 'text-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };

```

# frontend/src/components/ui/separator.tsx
```tsx
import * as React from 'react';
import { cn } from '@/lib/utils';

export interface SeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  decorative?: boolean;
}

export function Separator({
  className,
  orientation = 'horizontal',
  decorative = true,
  ...props
}: SeparatorProps) {
  return (
    <div
      role={decorative ? 'none' : 'separator'}
      aria-orientation={orientation}
      className={cn(
        'shrink-0 bg-border',
        orientation === 'horizontal' ? 'h-[1px] w-full' : 'h-full w-[1px]',
        className
      )}
      {...props}
    />
  );
}

```

# frontend/src/components/ui/button.tsx
```tsx
import * as React from 'react';
import { Slot } from '@radix-ui/react-slot';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive:
          'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline:
          'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary:
          'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button';
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = 'Button';

export { Button, buttonVariants };

```

# frontend/src/components/ui/sheet.tsx
```tsx
'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';

const Sheet = React.forwardRef<
  HTMLDivElement,
  {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children?: ReactNode;
  }
>(({ className, open, onOpenChange, children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      {...props}
      className={cn(className)}
      style={{
        display: open ? 'block' : 'none',
      }}
    >
      {children}
    </div>
  );
});
Sheet.displayName = 'Sheet';

const SheetTrigger = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(className)}
      {...props}
    >
      {props.children}
    </button>
  )
);
SheetTrigger.displayName = 'SheetTrigger';

const SheetContent = React.forwardRef<
  HTMLDivElement,
  {
    children?: ReactNode;
    onClose?: () => void;
  }
>(({ className, children, onClose, ...props }, ref) => (
    <div
      ref={ref}
      {...props}
      className={cn(
        'fixed inset-0 z-50 flex',
        'bg-background/95 backdrop-blur-sm',
        'p-6',
        className
      )}
    >
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Evidence</h2>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>
      <div className="max-h-[70vh] overflow-y-auto">
        {children}
      </div>
    </div>
  );
});
SheetContent.displayName = 'SheetContent';

const SheetHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      {...props}
      className={cn(className)}
    >
      {props.children}
    </div>
  );
});
SheetHeader.displayName = 'SheetHeader';

const SheetTitle = React.forwardRef<HTMLHeadingElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      {...props}
      className={cn('text-lg font-semibold', className)}
    >
      {props.children}
    </h3>
  );
});
SheetTitle.displayName = 'SheetTitle';

export { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle };

```

# frontend/src/components/ui/label.tsx
```tsx
import * as React from 'react';
import { cn } from '@/lib/utils';

export interface LabelProps
  extends React.LabelHTMLAttributes<HTMLLabelElement> {}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(
  ({ className, ...props }, ref) => (
      <label
        ref={ref}
        className={cn(
          'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
          className,
        )}
        {...props}
      />
  ),
);
Label.displayName = 'Label';

export { Label };

```

# frontend/src/components/ui/confidence-ring.tsx
```tsx
'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ConfidenceRingProps {
  confidence: number;
  size?: 'sm' | 'md' | 'lg';
}

export function ConfidenceRing({ confidence, size = 'md' }: ConfidenceRingProps) {
  const getRingColor = () => {
    if (confidence >= 0.85) return 'ring-green-500';
    if (confidence >= 0.70) return 'ring-amber-500';
    return 'ring-red-500 ring-opacity-0 ring-offset-0';
  };

  const ringColor = getRingColor();
  const sizeClasses = {
    sm: 'ring-2',
    md: 'ring-4',
    lg: 'ring-6',
  };

  return (
    <div
      className={cn(
        'rounded-full transition-all duration-500',
        ringColor,
        sizeClasses[size]
      )}
    >
      {children}
    </div>
  );
}

```

# frontend/src/components/chat/TypingIndicator.tsx
```tsx
import * as React from 'react';
import type { TypingIndicatorProps } from '@/types';

export function TypingIndicator({
  isVisible = true,
  text = 'Agent is typing...',
}: TypingIndicatorProps) {
  if (!isVisible) {
    return null;
  }

  return (
    <div className="flex items-center gap-1 text-sm text-muted-foreground px-4 py-2">
      <span>{text}</span>
      <div className="flex gap-1">
        <span className="animate-bounce" style={{ animationDelay: '0ms' }}>
          ●
        </span>
        <span className="animate-bounce" style={{ animationDelay: '150ms' }}>
          ●
        </span>
        <span className="animate-bounce" style={{ animationDelay: '300ms' }}>
          ●
        </span>
      </div>
    </div>
  );
}

```

# frontend/src/components/chat/ChatWidget.tsx
```tsx
'use client';

import * as React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { useChatStore } from '@/stores/chatStore';
import { Button } from '@/components/ui/button';
import { LogOut, RefreshCw } from 'lucide-react';

export function ChatWidget() {
  const { sessionId, isTyping, createSession, disconnect } =
    useChatStore();

  const handleSessionCreate = async () => {
    try {
      await createSession();
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnect();
    } catch (error) {
      console.error('Failed to disconnect:', error);
    }
  };

  React.useEffect(() => {
    const storedSessionId = localStorage.getItem('session_id');

    if (storedSessionId) {
      useChatStore.setState({ sessionId: storedSessionId });
    } else {
      handleSessionCreate();
    }
  }, []);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl h-[80vh] flex flex-col">
        <ChatHeader />

        <CardContent className="flex-1 overflow-hidden p-0">
          <ChatMessages />
        </CardContent>

        <ChatInput
          onSendMessage={async (content) => {
            const { sendMessage } = useChatStore.getState();
            await sendMessage(content);
          }}
          disabled={!sessionId || !isTyping}
          isLoading={isTyping}
        />

        <div className="border-t bg-muted px-4 py-2 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>
              Session ID: {sessionId?.slice(0, 8)}...
            </span>
            {sessionId && (
              <span>• {useChatStore.getState().messages.length} messages</span>
            )}
          </div>
          <div className="flex items-center gap-2">
            {sessionId && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleSessionCreate}
                title="New session"
              >
                <RefreshCw className="w-4 h-4" />
              </Button>
            )}
            {sessionId && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleDisconnect}
                title="Disconnect"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

```

# frontend/src/components/chat/ChatMessage.tsx
```tsx
'use client';

import * as React from 'react';
import { Bot, User } from 'lucide-react';
import { format } from 'date-fns';
import { Separator } from '@/components/ui/separator';
import { ConfidenceRing } from '@/components/ui/confidence-ring';
import { ThinkingState } from './ThinkingState';
import type { ChatMessageProps } from '@/types';
import { useChatStore } from '@/stores/chatStore';

export function ChatMessage({ message, showSources = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const { isThinking } = useChatStore();

  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <div className="bg-muted text-muted-foreground text-sm px-4 py-2 rounded-lg">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0">
          <ConfidenceRing confidence={message.confidence || 0}>
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
          </ConfidenceRing>
        </div>
      )}

      <div className={`max-w-[80%] space-y-2 ${isUser ? 'text-right' : 'text-left'}`}>
        {isThinking && <ThinkingState isThinking={true} />}

        <div
          className={`rounded-lg px-4 py-3 ${
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted text-muted-foreground'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>

        {showSources && message.sources && message.sources.length > 0 && (
          <details className="text-xs text-muted-foreground space-y-1">
            <summary className="cursor-pointer hover:text-foreground">
              {message.sources.length} source(s)
            </summary>
            <div className="mt-2 space-y-2 pl-4">
              {message.sources.map((source, idx) => (
                <div key={idx} className="border-l-2 border-muted pl-3">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">
                      Confidence: {(source.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="line-clamp-3 mt-1">
                    {source.content}
                  </p>
                </div>
              ))}
            </div>
          </details>
        )}

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>{format(new Date(message.timestamp), 'h:mm a')}</span>
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
          <User className="w-5 h-5 text-secondary-foreground" />
        </div>
      )}
    </div>
  );
}

```

# frontend/src/components/chat/ChatMessages.tsx
```tsx
import * as React from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';
import { useChatStore } from '@/stores/chatStore';

export function ChatMessages() {
  const { messages, isTyping } = useChatStore();
  const scrollAreaRef = React.useRef<HTMLDivElement>(null);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  if (messages.length === 0 && !isTyping) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground">
        <p className="text-center">
          Welcome to Singapore SMB Support Agent.
          <br />
          Ask me anything about our products, services, or policies.
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1" ref={scrollAreaRef}>
      <div className="p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            showSources
          />
        ))}

        {isTyping && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>
    </ScrollArea>
  );
}

```

# frontend/src/components/chat/ChatInput.tsx
```tsx
import * as React from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import type { ChatInputProps } from '@/types';

export function ChatInput({
  onSendMessage,
  disabled = false,
  isLoading = false,
  maxLength = 5000,
  placeholder = 'Type your message here...',
}: ChatInputProps) {
  const [message, setMessage] = React.useState('');
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = message.trim();

    if (trimmed.length > 0 && !disabled && !isLoading) {
      onSendMessage(trimmed);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;

    if (newValue.length <= maxLength) {
      setMessage(newValue);

      // Auto-resize textarea
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
      }
    }
  };

  React.useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [message]);

  const remainingChars = maxLength - message.length;
  const isNearLimit = remainingChars < 100;
  const isAtLimit = remainingChars <= 0;

  return (
    <div className="border-t bg-background p-4">
      <div className="space-y-2">
        <Label htmlFor="chat-input" className="sr-only">
          Message input
        </Label>
        <div className="flex gap-2">
          <Textarea
            ref={textareaRef}
            id="chat-input"
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isLoading}
            className="min-h-[60px] max-h-[200px] resize-none"
            aria-label="Message input"
          />
          <Button
            onClick={handleSend}
            disabled={disabled || isLoading || message.trim().length === 0}
            size="icon"
            className="h-[60px] w-[60px] flex-shrink-0"
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
        <div
          className={cn(
            'text-xs flex justify-between',
            isNearLimit && !isAtLimit && 'text-amber-500',
            isAtLimit && 'text-red-500',
          )}
        >
          <span className="text-muted-foreground">
            {isLoading ? 'Sending...' : 'Press Enter to send, Shift+Enter for new line'}
          </span>
          <span>
            {message.length} / {maxLength}
          </span>
        </div>
      </div>
    </div>
  );
}

```

# frontend/src/components/chat/EvidenceSheet.tsx
```tsx
'use client';

import * as React from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { Copy, Check } from 'lucide-react';
import type { Source } from '@/types';

export interface EvidenceSheetProps {
  source: Source;
  isOpen: boolean;
  onClose: () => void;
}

export function EvidenceSheet({ source, isOpen, onClose }: EvidenceSheetProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(source.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="max-w-2xl">
        <SheetHeader>
          <SheetTitle>Source Evidence</SheetTitle>
        </SheetHeader>
        <div className="p-6 space-y-4">
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground">
              File: {source.metadata?.file_name || 'Unknown'}
            </div>
            <div className="text-sm text-muted-foreground">
              Confidence: {(source.score * 100).toFixed(1)}%
            </div>
          </div>

          <div className="bg-muted rounded-lg p-4 font-mono text-sm">
            {source.content}
          </div>

          <button
            onClick={handleCopy}
            className="w-full flex items-center justify-center gap-2 rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground transition-colors"
            type="button"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-green-500" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Source Text</span>
              </>
            )}
          </button>
        </div>
      </SheetContent>
    </Sheet>
  );
}

```

# frontend/src/components/chat/ChatHeader.tsx
```tsx
'use client';

import * as React from 'react';
import { Clock, Globe, Trash2 } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useChatStore } from '@/stores/chatStore';
import { SessionPulse } from './SessionPulse';
import type { BusinessHours, ChatHeaderProps } from '@/types';

export function ChatHeader() {
  const { connectionStatus } = useChatStore();

  const getBusinessHours = (): BusinessHours => {
    const now = new Date();
    const hour = now.getHours();
    const isBusinessHours = hour >= 9 && hour < 18;
    const day = now.toLocaleDateString('en-SG', { weekday: 'long' });
    const time = now.toLocaleTimeString('en-SG', {
      hour: '2-digit',
      minute: '2-digit',
    });

    return {
      is_open: isBusinessHours,
      business_hours: '9:00 AM - 6:00 PM (SGT)',
      current_time: time,
      timezone: 'Asia/Singapore',
    };
  };

  const hours = getBusinessHours();
  const isConnected = connectionStatus === 'connected';
  const isOnline = hours.is_open && isConnected;
  const statusColor = isOnline ? 'bg-green-500' : 'bg-amber-500';

  return (
    <CardHeader className="px-6 py-4 border-b">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <SessionPulse expiresAt={new Date(Date.now() + 30 * 60000)} />
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${statusColor}`}></div>
                <span className="font-semibold">
                  Singapore SMB Support Agent
                </span>
              </div>
            </div>
          </div>

          <Badge
            variant={isOnline ? 'default' : 'outline'}
            className={isOnline ? 'bg-primary' : 'bg-secondary'}
          >
            {isOnline ? 'Online' : 'Offline'}
          </Badge>
        </div>

        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <Clock className="w-4 h-4" />
            <span>{hours.business_hours}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Globe className="w-4 h-4" />
            <span>{hours.timezone}</span>
          </div>
          <div className="text-xs">
            {hours.current_time}
          </div>
        </div>
      </div>
    </CardHeader>
  );
}

```

# frontend/src/components/chat/ThinkingState.tsx
```tsx
'use client';

import * as React from 'react';
import { Loader2 } from 'lucide-react';

interface ThinkingStateProps {
  isThinking: boolean;
}

const THOUGHT_STEPS = [
  { text: "Scanning Knowledge Base...", icon: Loader2 },
  { text: "Cross-referencing Policies...", icon: Loader2 },
  { text: "Formatting Response...", icon: Loader2 },
];

export function ThinkingState({ isThinking }: ThinkingStateProps) {
  const [currentStep, setCurrentStep] = React.useState(0);

  React.useEffect(() => {
    if (isThinking) {
      const interval = setInterval(() => {
        setCurrentStep((prev) => (prev + 1) % THOUGHT_STEPS.length);
      }, 2000); // 2s per step
      return () => clearInterval(interval);
    } else {
      setCurrentStep(0);
    }
  }, [isThinking]);

  if (!isThinking) return null;

  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <div className="flex gap-1">
        <ThinkingDots />
      </div>
      <span>{THOUGHT_STEPS[currentStep].text}</span>
    </div>
  );
}

```

# frontend/src/components/chat/SessionPulse.tsx
```tsx
'use client';

import * as React from 'react';
import { Trash2 } from 'lucide-react';

interface SessionPulseProps {
  expiresAt: Date;
  onExtend?: () => void;
  onWipe?: () => void;
}

export function SessionPulse({ expiresAt, onExtend, onWipe }: SessionPulseProps) {
  const [timeLeft, setTimeLeft] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const diff = expiresAt.getTime() - now.getTime();
      const minutes = Math.max(0, Math.floor(diff / 60000));
      setTimeLeft(minutes);
    }, 1000);

    return () => clearInterval(interval);
  }, [expiresAt]);

  const getPhase = () => {
    if (timeLeft > 15) return { color: 'bg-green-500', pulse: 'animate-pulse' };
    if (timeLeft > 5) return { color: 'bg-amber-500', pulse: 'animate-pulse' };
    return { color: 'bg-red-500', pulse: 'animate-ping' };
  };

  const phase = getPhase();

  return (
    <div className="relative">
      <div
        className={`w-3 h-3 rounded-full ${phase.color} ${phase.pulse}`}
        title={`${timeLeft} minutes remaining`}
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-[10px] font-bold text-white">
          {timeLeft}m
        </span>
      </div>
    </div>
  );
}

```

# frontend/src/stores/chatStore.ts
```ts
/**
 * Zustand store for chat state management
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  Message,
  MessageRole,
  ChatRequest,
  ChatResponse,
} from '@/types';

interface ChatStore {
  // Session state
  sessionId: string | null;
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';

  // Messages
  messages: Message[];
  isTyping: boolean;

  // Trust & Thinking
  isThinking: boolean;

  // Evidence Sheet
  expandedCitation: number | null;

  // Evidence Sheet
  expandedCitation: number | null;

  // Actions
  setSessionId: (id: string) => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  setConnected: (connected: boolean) => void;
  setConnectionStatus: (
    status: 'connecting' | 'connected' | 'disconnected' | 'error',
  ) => void;
  setTyping: (typing: boolean) => void;

  // Trust & Thinking actions
  setThinking: (thinking: boolean) => void;

  // Evidence actions
  setExpandedCitation: (citation: number | null) => void;

  // Async actions
  sendMessage: (content: string) => Promise<void>;
  createSession: () => Promise<void>;
  disconnect: () => Promise<void>;
}

export const useChatStore = create<ChatStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      sessionId: null,
      isConnected: false,
      connectionStatus: 'disconnected',
      messages: [],
      isTyping: false,
      isThinking: false,

      // Session actions
      setSessionId: (id) => set({ sessionId: id }),

      // Message actions
      addMessage: (message) =>
        set((state) => ({
          messages: [...state.messages, message],
        })),

      updateMessage: (id, updates) =>
        set((state) => ({
          messages: state.messages.map((msg) =>
            msg.id === id ? { ...msg, ...updates } : msg,
          ),
        })),

      clearMessages: () => set({ messages: [] }),

      // Connection actions
      setConnected: (connected) => set({ isConnected: connected }),

      setConnectionStatus: (
        status: 'connecting' | 'connected' | 'disconnected' | 'error',
      ) => set({
        connectionStatus: status,
        isConnected: status === 'connected',
      }),

      setTyping: (typing) => set({ isTyping: typing }),

      // Trust & Thinking actions
      setThinking: (thinking: boolean) => set({ isThinking: thinking }),

      // Evidence actions
      setExpandedCitation: (citation: number | null) => set({ expandedCitation: citation }),

      // Async actions
      sendMessage: async (content) => {
        const { sessionId, addMessage, setTyping } = get();

        if (!sessionId) {
          console.error('No session ID. Cannot send message.');
          return;
        }

        // Add user message
        const userMessage: Message = {
          id: `msg-${Date.now()}-user`,
          role: 'user' as MessageRole,
          content,
          timestamp: new Date(),
        };

        addMessage(userMessage);
        setTyping(true);

        try {
          const { chatService } = await import('@/lib/api');

          const request: ChatRequest = {
            session_id: sessionId,
            message: content,
          };

          const response: ChatResponse = await chatService.sendMessage(request);

          // Add assistant message
          const assistantMessage: Message = {
            id: `msg-${Date.now()}-assistant`,
            role: 'assistant' as MessageRole,
            content: response.message,
            timestamp: new Date(),
            confidence: response.confidence,
            sources: response.sources,
          };

          addMessage(assistantMessage);

          if (response.escalated) {
            const escalatedMessage: Message = {
              id: `msg-${Date.now()}-system`,
              role: 'system' as MessageRole,
              content: response.ticket_id
                ? `Ticket created: ${response.ticket_id}`
                : 'Escalated to human support.',
              timestamp: new Date(),
            };
            addMessage(escalatedMessage);
          }
        } catch (error) {
          console.error('Failed to send message:', error);

          const errorMessage: Message = {
            id: `msg-${Date.now()}-error`,
            role: 'system' as MessageRole,
            content:
              'Failed to send message. Please try again.',
            timestamp: new Date(),
          };
          addMessage(errorMessage);
        } finally {
          setTyping(false);
        }
      },

      createSession: async () => {
        try {
          const { authService } = await import('@/lib/api');

          const session = await authService.createSession();
          const { sessionId } = session;

          set({ sessionId });
          localStorage.setItem('session_id', sessionId);

          return session;
        } catch (error) {
          console.error('Failed to create session:', error);
          throw error;
        }
      },

      disconnect: async () => {
        const { sessionId } = get();

        if (sessionId) {
          try {
            const { authService } = await import('@/lib/api');
            await authService.logout(sessionId);
          } catch (error) {
            console.error('Failed to disconnect:', error);
          }
        }

        localStorage.removeItem('session_id');
        set({
          sessionId: null,
          isConnected: false,
          connectionStatus: 'disconnected',
          messages: [],
          isTyping: false,
          isThinking: false,
        });
      },
    }),
    { name: 'chat-store' },
  ),
);

// Selectors
export const selectMessages = (state: ChatStore) => state.messages;
export const selectIsTyping = (state: ChatStore) => state.isTyping;
export const selectIsConnected = (state: ChatStore) => state.isConnected;
export const selectConnectionStatus = (state: ChatStore) => state.connectionStatus;
export const selectSessionId = (state: ChatStore) => state.sessionId;
export const selectIsThinking = (state: ChatStore) => state.isThinking;

```

# frontend/src/lib/api.ts
```ts
/**
 * API client for Singapore SMB Support Agent backend
 */

import type {
  UserRegisterRequest,
  UserLoginRequest,
  AuthResponse,
  Session,
  User,
  ChatRequest,
  ChatResponse,
  ErrorResponse,
  HealthCheck,
} from '@/types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * API Error class
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public error_code?: string,
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Helper function to handle API errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type');

  if (!contentType?.includes('application/json')) {
    throw new APIError(
      'Invalid response format',
      response.status,
    );
  }

  const data = await response.json();

  if (!response.ok) {
    const error: ErrorResponse = data;
    throw new APIError(
      error.detail || 'An error occurred',
      response.status,
      error.error_code,
    );
  }

  return data as T;
}

/**
 * Authentication service
 */
export const authService = {
  /**
   * Register a new user
   */
  register: async (
    request: UserRegisterRequest,
  ): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse<User>(response);
  },

  /**
   * Login user
   */
  login: async (
    request: UserLoginRequest,
  ): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse<AuthResponse>(response);
  },

  /**
   * Logout user
   */
  logout: async (
    session_id: string,
  ): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ session_id }),
    });

    return handleResponse<{ message: string }>(response);
  },

  /**
   * Get current user
   */
  getCurrentUser: async (
    session_id: string,
  ): Promise<User> => {
    const response = await fetch(
      `${API_BASE_URL}/auth/me?session_id=${session_id}`,
    );

    return handleResponse<User>(response);
  },

  /**
   * Create new session (anonymous)
   */
  createSession: async (): Promise<Session> => {
    const response = await fetch(`${API_BASE_URL}/auth/session/new`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return handleResponse<Session>(response);
  },
};

/**
 * Chat service
 */
export const chatService = {
  /**
   * Send chat message via REST API
   */
  sendMessage: async (
    request: ChatRequest,
  ): Promise<ChatResponse> => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    return handleResponse<ChatResponse>(response);
  },

  /**
   * Get session messages
   */
  getSession: async (
    session_id: string,
  ): Promise<{ session_id: string; messages: unknown[] }> => {
    const response = await fetch(
      `${API_BASE_URL}/chat/sessions/${session_id}`,
    );

    return handleResponse<{ session_id: string; messages: unknown[] }>(
      response,
    );
  },
};

/**
 * Health check service
 */
export const healthService = {
  /**
   * Check API health
   */
  check: async (): Promise<HealthCheck> => {
    const response = await fetch(`${API_BASE_URL.replace('/api/v1', '')}/health`);

    return handleResponse<HealthCheck>(response);
  },
};

export default {
  authService,
  chatService,
  healthService,
};

```

# frontend/src/lib/utils.ts
```ts
import { clsx, type ClassValue } from "clsx"

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

```

# frontend/src/lib/websocket.ts
```ts
/**
 * WebSocket client for real-time chat
 */

import type {
  WSMessage,
  WSRequest,
  WSConnected,
  WSResponse,
  WSError,
} from '@/types';

export interface WebSocketClientOptions {
  url: string;
  session_id: string;
  onMessage?: (message: WSMessage) => void;
  onError?: (error: Event) => void;
  onClose?: (event: CloseEvent) => void;
  onOpen?: () => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export type ConnectionStatus =
  | 'connecting'
  | 'connected'
  | 'disconnected'
  | 'error';

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private reconnectAttempts = 0;

  private readonly options: Required<WebSocketClientOptions>;
  private _status: ConnectionStatus = 'disconnected';

  constructor(options: WebSocketClientOptions) {
    this.options = {
      url: options.url,
      session_id: options.session_id,
      onMessage: options.onMessage,
      onError: options.onError,
      onClose: options.onClose,
      onOpen: options.onOpen,
      reconnectInterval: options.reconnectInterval || 3000,
      maxReconnectAttempts: options.maxReconnectAttempts || 10,
      heartbeatInterval: options.heartbeatInterval || 30000,
    };
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    return this._status;
  }

  /**
   * Update status and notify
   */
  private setStatus(status: ConnectionStatus) {
    this._status = status;
  }

  /**
   * Connect to WebSocket server
   */
  connect() {
    this.setStatus('connecting');
    this.reconnectAttempts = 0;

    try {
      this.ws = new WebSocket(
        `${this.options.url}?session_id=${this.options.session_id}`,
      );

      this.setupEventListeners();
    } catch (error) {
      this.setStatus('error');
      this.options.onError?.(
        new ErrorEvent('error', { error } as any),
      );
      this.scheduleReconnect();
    }
  }

  /**
   * Setup WebSocket event listeners
   */
  private setupEventListeners() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.setStatus('connected');
      this.reconnectAttempts = 0;
      this.options.onOpen?.();
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WSMessage = JSON.parse(event.data);

        if (message.type === 'pong') {
          return;
        }

        this.options.onMessage?.(message);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      this.setStatus('error');
      this.options.onError?.(error);
    };

    this.ws.onclose = (event) => {
      this.setStatus('disconnected');
      this.stopHeartbeat();
      this.options.onClose?.(event);

      if (!event.wasClean) {
        this.scheduleReconnect();
      }
    };
  }

  /**
   * Send message to server
   */
  send(message: WSRequest) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }

  /**
   * Send chat message
   */
  sendChatMessage(content: string) {
    this.send({
      type: 'message',
      message: content,
    });
  }

  /**
   * Send ping
   */
  sendPing() {
    this.send({
      type: 'ping',
    });
  }

  /**
   * Disconnect from server
   */
  disconnect() {
    this.stopReconnect();
    this.stopHeartbeat();

    if (this.ws) {
      this.send({
        type: 'disconnect',
      });
      this.ws.close();
      this.ws = null;
    }

    this.setStatus('disconnected');
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect() {
    if (
      this.reconnectAttempts >= this.options.maxReconnectAttempts ||
      this._status === 'connected'
    ) {
      return;
    }

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, this.options.reconnectInterval);
  }

  /**
   * Stop reconnection attempts
   */
  private stopReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Start heartbeat/ping-pong
   */
  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.sendPing();
    }, this.options.heartbeatInterval);
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }
}

export default WebSocketClient;

```

# frontend/src/types/index.ts
```ts
/**
 * TypeScript type definitions for Singapore SMB Support Agent frontend
 */

// Message types
export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  confidence?: number;
  sources?: Source[];
}

// Source type for RAG citations
export interface Source {
  content: string;
  metadata: Record<string, unknown>;
  score: number;
}

// Chat API types
export interface ChatRequest {
  session_id: string;
  message: string;
  language?: string;
}

export interface ChatResponse {
  session_id: string;
  message: string;
  role: string;
  confidence: number;
  sources: Source[];
  requires_followup: boolean;
  escalated: boolean;
  ticket_id?: string;
}

// Authentication types
export interface UserRegisterRequest {
  email: string;
  password: string;
  consent_given: boolean;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface Session {
  session_id: string;
  user_id?: number;
  email?: string;
  created_at: string;
  expires_in?: string;
  expires_at?: Date;
}

export interface ChatHeaderProps {
  isOnline?: boolean;
  businessHours?: BusinessHours;
  agentName?: string;
  sessionExpiresAt?: Date;
  onExtend?: () => void;
  onWipe?: () => void;
}

// WebSocket message types
export interface WSConnected {
  type: 'connected';
  session_id: string;
  message: string;
}

export interface WSResponse {
  type: 'response';
  session_id: string;
  message: string;
  confidence: number;
  sources: Source[];
  requires_followup: boolean;
  escalated: boolean;
  ticket_id?: string;
}

export interface WSError {
  type: 'error';
  message: string;
}

export interface WSPong {
  type: 'pong';
}

export interface WSPing {
  type: 'ping';
}

export interface WSMessageRequest {
  type: 'message';
  message: string;
}

export interface WSDisconnect {
  type: 'disconnect';
}

export type WSMessage = WSConnected | WSResponse | WSError | WSPong;
export type WSRequest = WSMessageRequest | WSPing | WSDisconnect;

// Business hours type
export interface BusinessHours {
  is_open: boolean;
  business_hours: string;
  current_time: string;
  timezone: string;
}

// Health check type
export interface HealthCheck {
  status: string;
  timestamp: string;
  services: Record<string, string>;
}

// Error types
export interface ErrorResponse {
  detail: string;
  error_code?: string;
  timestamp: string;
}

// UI component types
export interface ChatHeaderProps {
  isOnline?: boolean;
  businessHours?: BusinessHours;
  agentName?: string;
}

export interface ChatMessageProps {
  message: Message;
  showSources?: boolean;
}

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  isLoading?: boolean;
  maxLength?: number;
  placeholder?: string;
}

export interface TypingIndicatorProps {
  isVisible?: boolean;
  text?: string;
}

```

