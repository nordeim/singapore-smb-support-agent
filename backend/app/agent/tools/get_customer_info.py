"""Get customer info tool for Singapore SMB Support Agent."""

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
    customer: CustomerInfo | None = Field(None, description="Customer information")
    message: str | None = Field(None, description="Additional information")


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
            (User.email == customer_identifier) & (not User.is_deleted)
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
