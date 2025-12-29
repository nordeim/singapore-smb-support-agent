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
