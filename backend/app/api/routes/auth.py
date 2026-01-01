"""Authentication API routes for Singapore SMB Support Agent (MVP - Session-based)."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db, get_memory_manager
from app.models.database import Conversation, User
from app.models.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

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
        from uuid import uuid4

        from passlib.context import CryptContext

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
    session_id: str | None = None,
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
