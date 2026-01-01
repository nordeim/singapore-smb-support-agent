"""Escalate to human tool for Singapore SMB Support Agent."""


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
    user_id: int | None = Field(None, description="User ID (optional)")


class EscalationTicket(BaseModel):
    """Escalation ticket model."""

    ticket_id: str
    reason: str
    status: str
    assigned_to: str | None
    estimated_response_time: str


class EscalateToHumanOutput(BaseModel):
    """Output for escalate_to_human tool."""

    success: bool = Field(..., description="Whether escalation was successful")
    ticket: EscalationTicket | None = Field(None, description="Ticket information")
    message: str = Field(..., description="Human-readable message")


async def escalate_to_human(
    reason: str,
    urgency: str = "normal",
    session_id: str = "",
    user_id: int | None = None,
    db: AsyncSession | None = None,
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
        from datetime import datetime

        from app.models.database import Conversation, SupportTicket

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


def get_escalate_to_human_tool(db: AsyncSession | None = None):
    """Factory function to create escalate_to_human tool for Pydantic AI."""
    from pydantic_ai import Tool

    async def tool_wrapper(
        reason: str,
        urgency: str = "normal",
        session_id: str = "",
        user_id: int | None = None,
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
