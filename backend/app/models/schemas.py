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
