"""Domain models for Singapore SMB Support Agent."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
    auto_expiry_at: datetime | None = None
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
    ended_at: datetime | None = None
    summary_count: int = 0
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    confidence: float | None = None
    sources: str | None = None
    created_at: datetime


class ConversationSummary(BaseModel):
    id: int
    conversation_id: int
    summary: str
    message_range_start: int
    message_range_end: int
    embedding_vector: bytes | None = None
    metadata: str | None = None
    created_at: datetime


class SupportTicket(BaseModel):
    id: int
    conversation_id: int
    reason: str
    status: TicketStatus = TicketStatus.OPEN
    assigned_to: str | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
